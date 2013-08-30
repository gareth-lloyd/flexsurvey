from collections import OrderedDict, defaultdict
from datetime import datetime
from pytz import timezone

import openpyxl
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import MultiValueDict
from django.conf import settings

from survey import models

SPREADSHEETS_ROOT = getattr(settings, 'SPREADSHEETS_ROOT', '.')
TIMEZONE = timezone(settings.TIME_ZONE)

def export_subjects(survey, queryset):
    """Return {subject: data_dict, ...} OrderedDict populated with data for
    each subject in queryset.

    The export data for each subject will be in a MultiValueDict to handle the
    legal case where a subject has multiple facts recorded for a single desired
    fact.
    """
    subject_type = ContentType.objects.get_for_model(queryset.model)
    export_tuples = [(subject, _do_export(survey, subject_type, subject.pk))
            for subject in queryset]
    return OrderedDict(export_tuples)

def export_subject(survey, subject):
    """Return a {code: data, ...} dict populated with data for this subject,
    with the data in a MultiValueDict.
    """
    subject_type = ContentType.objects.get_for_model(subject)
    return _do_export(survey, subject_type, subject.pk)

def _do_export(survey, subject_type, pk):
    facts = models.Fact.objects\
            .filter(survey=survey, content_type=subject_type, object_id=pk)\
            .select_related('desired_fact')

    export_data = MultiValueDict()
    for fact in facts:
        export_data.appendlist(fact.desired_fact.code, fact.data)
    return export_data

def generate_spreadsheet_definition(survey):
    sdfs = survey.surveydesiredfact_set.all()\
            .select_related('desired_fact', 'fact_group')\
            .order_by('weight')

    dfs_by_type = defaultdict(set)
    dfs_by_group = defaultdict(list)
    for sdf in sdfs:
        df = sdf.desired_fact
        dfs_by_type[df.content_type].add(df)
        dfs_by_group[sdf.fact_group].append(df)

    spreadsheet = defaultdict(list)
    for content_type, dfs_for_type in dfs_by_type.iteritems():
        for group, group_dfs in dfs_by_group.iteritems():
            codes = [df.code for df in group_dfs if df in dfs_for_type]
            if codes:
                try:
                    model = content_type.model_class()
                    codes = model.survey_identifiers + codes
                except AttributeError:
                    pass
                spreadsheet[content_type].append({
                    'title': group.heading[:30], # max worksheet title length
                    'codes': codes
                })
    return spreadsheet

class ExcelExport(object):
    """
    Takes a spreadsheet definition in the following form and uses it to output
    an Excel spreadsheet containing data for the given survey.
    SPREADSHEET_DEFINIION = {
        <ContentType object> : [
            {
                'title': <worksheet title>, 
                'codes': [
                    <DesiredFact code 1>,
                    <DesiredFact code 2>,
                    ...
                ],
            },
            ...
        }
    """
    def __init__(self, spreadsheet_defn, output_translations=None,
            allow_blank=None, multi_row_data=None):

        self.workbook = openpyxl.Workbook(optimized_write=True)
        self.spreadsheet_defn = spreadsheet_defn
        self.output_translations = output_translations or {}
        self.allow_blank = set(allow_blank or [])
        self.multi_row_data = multi_row_data or {}

    def _filename(self):
        now = TIMEZONE.localize(datetime.now())
        return "export__{date}.xlsx".format(
                date=now.strftime('%Y_%m_%d_%H%M'))

    def create_worksheet(self, title, header_row, translations):
        worksheet = self.workbook.create_sheet()
        worksheet.title = title

        final_header_row = []
        for heading in header_row:
            if isinstance(heading, dict):
                heading = heading['code']
            final_header_row.append(translations.get(heading, heading))
        worksheet.append(final_header_row)

        return worksheet

    def make_cell(self, data, code, **kwargs):
        values = data.getlist(code)
        if values == []:
            if not self.allow_blank or code in self.allow_blank:
                values = ['']
            else:
                values = ['0']

        return ', '.join(map(str, values))

    def make_row(self, data, codes, **kwargs):
        return [self.make_cell(data, code, **kwargs) for code in codes]

    def make_multi_rows(self, multi_key, data, codes):
        rows = []
        while data.getlist(multi_key):
            rows.append(self.make_row(data, codes))
            data.getlist(multi_key).pop()
        return rows

    def append_row(self, worksheet, row_data):
        worksheet.append(row_data)

    def output_data(self, worksheet, title, codes, subjects_data):
        if title in self.multi_row_data:
            multi_key = self.multi_row_data[title]
            for subject, data in subjects_data.iteritems():
                for row in self.make_multi_rows(multi_key, data, codes):
                    self.append_row(worksheet, row)
        else:
            for subject, data in subjects_data.iteritems():
                self.append_row(worksheet, self.make_row(data, codes))

    def get_subjects_data(content_type):
        raise NotImplemented

    def do_export(self):
        for content_type, sheet_defns in self.spreadsheet_defn.iteritems():
            for sheet_defn in sheet_defns:
                codes, title = sheet_defn['codes'], sheet_defn['title']

                trans = self.output_translations.get(title, {})
                worksheet = self.create_worksheet(title, codes, trans)

                subjects_data = self.get_subjects_data(content_type)
                self.output_data(worksheet, title, codes, subjects_data)

        filename = self._filename()
        path = ''.join([SPREADSHEETS_ROOT, '/', filename])
        self.workbook.save(filename=path)
        return filename, path

