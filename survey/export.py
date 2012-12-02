from collections import OrderedDict
from survey import models
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import MultiValueDict

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



