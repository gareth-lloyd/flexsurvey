from unittest import TestCase
from django.utils.datastructures import MultiValueDict

from survey.tests.utils import SurveyTestCase
from survey.models import Fact, Project
from survey.export import export_subject, export_subjects, ExcelExport

class ExportTests(SurveyTestCase):
    def setUp(self):
        super(ExportTests, self).setUp()
        self.login()
        Fact.objects.create(subject=self.subject, survey=self.survey,
                desired_fact=self.desired_fact, data='a', created_by=self.user,
                updated_by=self.user)

    def test_export(self):
        export_data = export_subject(self.survey, self.subject)
        self.assertEquals(1, len(export_data))
        self.assertEquals('a', export_data[self.desired_fact.code])

    def test_export_multiple_fact_values(self):
        Fact.objects.create(subject=self.subject, survey=self.survey,
                desired_fact=self.desired_fact, data='b', created_by=self.user,
                updated_by=self.user)

        export_data = export_subject(self.survey, self.subject)
        self.assertEquals(1, len(export_data))

        data = set(export_data.getlist(self.desired_fact.code))
        self.assertEquals(set(['a', 'b']), data)

    def test_export_subjects(self):
        qs = Project.objects.filter(name='subject_standin')
        export = export_subjects(self.survey, qs)
        export_data = export[self.subject]
        self.assertEquals(1, len(export_data))
        self.assertEquals('a', export_data[self.desired_fact.code])


CODE = 'code1'
MULTI_CODE = 'code_multi'

class ExcelExportTests(TestCase):
    def setUp(self):
        self.data = MultiValueDict(
            [
                (CODE, ['val']),
                (MULTI_CODE, ['val1', 'val2']),
            ]
        )
        self.export = ExcelExport({})

    def test_make_cell_non_present_allow_blank_implicit(self):
        self.assertEquals('', self.export.make_cell(self.data, 'not_present'))

    def test_make_cell_non_present_allow_blank_explicit(self):
        self.export.allow_blank = {'not_present'}
        self.assertEquals('', self.export.make_cell(self.data, 'not_present'))

    def test_make_cell_non_present_not_allow_blank(self):
        self.export.allow_blank = {CODE}
        self.assertEquals('0', self.export.make_cell(self.data, 'not_present'))

    def test_make_cell_present_single_value(self):
        self.assertEquals('val', self.export.make_cell(self.data, CODE))

    def test_make_cell_present_multi_value(self):
        self.assertEquals('val1, val2', self.export.make_cell(self.data, MULTI_CODE))

