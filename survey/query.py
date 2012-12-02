from django.contrib.contenttypes.models import ContentType
from survey.models import Fact

def _get_facts(survey, content_type=None, subjects_qs=None, desired_facts=None, value=None):
    # if content_type is specified, query for all subjects of that type
    if content_type:
        facts = Fact.objects.filter(survey=survey, content_type=content_type)
    elif subjects_qs is not None:
        content_type = ContentType.objects.get_for_model(subjects_qs.model)
        object_ids = list(subjects_qs.values_list('pk', flat=True))
        facts = Fact.objects.filter(survey=survey, content_type=content_type,
                object_id__in=object_ids)
    else:
        raise ValueError('Ambiguous arguments.')

    if desired_facts:
        if not isinstance(desired_facts, (list, tuple)):
            desired_facts = [desired_facts]
        facts = facts.filter(desired_fact__in=desired_facts)

    if value is not None:
        facts = facts.filter(data=value)

    return facts

def _get_subject_ids_for_facts(facts):
    return facts.distinct('object_id').values_list('object_id', flat=True)


def get_subjects(survey, content_type, desired_facts=None, value=None):
    """For a given survey, return all subjects of the specified type.

    If a desired fact is specified, only return those subjects that have
    data for that fact.

    If a value is specified, only return subjects whose data matches the
    value.

    Desired fact and value can be specified together.
    """
    facts = _get_facts(survey, content_type=content_type, 
            desired_facts=desired_facts, value=value)
    subject_ids = _get_subject_ids_for_facts(facts)
    return content_type.model_class().objects.filter(pk__in=subject_ids)

def sum_facts(survey, subjects_qs, desired_facts):
    """Get all the facts matching a desired fact for a particular
    survey and content_type. Sum the facts' data.
    """
    to_sum = _get_facts(survey, subjects_qs=subjects_qs,
            desired_facts=desired_facts)
    return sum([fact.typed_data for fact in to_sum])

def sum_facts_where(survey, subjects_qs, sum_dfs, match_df=None,
        match_value=None):
    """Find all subjects whose facts match the criteria. For those
    subjects, obtain facts related to sum_df and sum them.

    This is useful in cases where you want to query on one desired fact,
    and sum something else for all matching subjects. E.g. find all 
    households with a colour television, and sum the monthly income of 
    those households.
    """
    if not isinstance(sum_dfs, (list, tuple)):
        sum_dfs = [sum_dfs]

    # first get all subject_ids that have the required fact
    facts = _get_facts(survey, subjects_qs=subjects_qs,
            desired_facts=match_df, value=match_value)

    subject_ids = _get_subject_ids_for_facts(facts)

    # Get all the sum_dfs for these subjects, and sum them
    if subject_ids:
        content_type = facts[0].content_type

        to_sum = Fact.objects.filter(survey=survey, content_type=content_type,
                desired_fact__in=sum_dfs, object_id__in=subject_ids)

        return sum([fact.typed_data for fact in to_sum])
    else:
        return 0

def get_number_of_subjects_where(survey, subjects_qs, match_df, match_value):
    """Return the number of subjects about which we have recorded
    facts matching these parameters.
    """
    facts = _get_facts(survey, subjects_qs=subjects_qs, 
            desired_facts=match_df, value=match_value)
    return len(_get_subject_ids_for_facts(facts))
