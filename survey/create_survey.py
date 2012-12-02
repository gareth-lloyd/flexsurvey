"""Create the desired facts from a structured python dictionary. This
allows surveys to be defined in code.
"""
from survey.models import (DesiredFactGroup, DesiredFact, SurveyDesiredFact,
        FactOption)


def create_desired_facts(survey, desired_facts_defns):
    """
    desired_facts_defns has the format:
    {
        <content type>: [
            {
                'heading': <heading>,
                'desired_facts': [
                    {'code': 'df1', ...},
                    ...
                ]
            },
            ...
        ],
        ...
    }

    """
    for subject_type, fact_groups in desired_facts_defns.iteritems():
        for weight, fact_group_defn in enumerate(fact_groups):
            dfg, _ = DesiredFactGroup.objects\
                    .get_or_create(heading=fact_group_defn['heading'],
                            defaults={'weight': weight})
            for weight, d in enumerate(fact_group_defn['desired_facts']):
                df, _ = DesiredFact.objects.get_or_create(
                        code=d['code'],
                        label=d['label'],
                        help_text=d.get('help_text', None),
                        data_type=d.get('data_type', 'S'),
                        required=d.get('required', True),
                        content_type=subject_type)

                for code, description in d.get('choices', []):
                    FactOption.objects.get_or_create(
                            code=code,
                            description=description,
                            desired_fact=df)

                SurveyDesiredFact.objects.get_or_create(
                        survey=survey,
                        weight=weight,
                        desired_fact=df,
                        fact_group=dfg)
