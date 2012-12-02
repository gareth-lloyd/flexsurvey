from survey.tests.utils import SurveyTestCase

from survey.query import get_subjects, sum_facts_where, sum_facts
from survey.models import Project, Survey, DesiredFact

class QueryTests(SurveyTestCase):
    def setUp(self):
        super(QueryTests, self).setUp()

        self.login()

        self.desired_fact.data_type = 'I'
        self.desired_fact.save()
        self.subject2 = Project.objects.create(name='subject_standin2')

    def test_get_subjects_no_subjects(self):
        self.assertEquals(
                [],
                list(get_subjects(self.survey, self.content_type))
            )

    def test_get_subjects(self):
        "with no where clause, should return all subjects with facts"
        self._save_fact('01')
        self.assertEquals(
                [self.subject],
                list(get_subjects(self.survey, self.content_type))
            )

    def test_get_subjects_where(self):
        "only expect facts with data that matches the where clause"
        self._save_fact('01')
        subjects = get_subjects(self.survey, self.content_type,
                desired_facts=self.desired_fact, value='01')

        self.assertEquals(
                [self.subject],
                list(subjects)
            )

    def test_get_subjects_where_no_match(self):
        "empty queryset should be returned if no matches"
        self._save_fact('01')
        subjects = get_subjects(self.survey, self.content_type,
                desired_facts=self.desired_fact, value='02')

        self.assertEquals(
                [],
                list(subjects)
            )

    def test_facts_for_different_survey_not_counted(self):
        "must discriminate by survey"
        # associate self.subject with self.survey
        self._save_fact('01', subject=self.subject, survey=self.survey)

        # associate self.subject2 with a different survey
        survey2 = Survey.objects.create(name='other', project=self.project)
        self._save_fact('01', subject=self.subject2, survey=survey2)

        subjects = get_subjects(self.survey, self.content_type,
                desired_facts=self.desired_fact, value='01')

        self.assertTrue(self.subject in subjects)
        self.assertFalse(self.subject2 in subjects)

    def test_get_subjects_where_multi_match(self):
        "Should get all matching subjects"
        self._save_fact('01', subject=self.subject)
        self._save_fact('01', subject=self.subject2)

        subjects = get_subjects(self.survey, self.content_type,
                desired_facts=self.desired_fact, value='01')

        self.assertEquals(
                set([self.subject2, self.subject]),
                set(subjects)
            )

    def test_sum_facts_where(self):
        self.desired_fact.data_type = 'I'
        self.desired_fact.save()

        self._save_fact('01', subject=self.subject)
        subjects_qs = Project.objects.filter(id=self.subject.id)
        total = sum_facts_where(self.survey, subjects_qs, match_df=self.desired_fact,
                match_value=None, sum_dfs=self.desired_fact)

        self.assertEquals(1, total)

    def test_sum_facts_where_multiple(self):
        match_df = self.desired_fact
        sum_df = DesiredFact.objects.create(code='code2',
                label='a', data_type='I', required=True,
                content_type=self.content_type)

        self._save_fact('01', subject=self.subject, desired_fact=match_df)
        self._save_fact('06', subject=self.subject, desired_fact=sum_df)

        self._save_fact('01', subject=self.subject2, desired_fact=match_df)
        self._save_fact('05', subject=self.subject2, desired_fact=sum_df)

        subjects_qs = Project.objects.filter(id__in=(self.subject.id, self.subject2.id))
        total = sum_facts_where(self.survey, subjects_qs=subjects_qs,
                match_df=match_df, match_value=None,
                sum_dfs=sum_df)

        self.assertEquals(11, total)

    def test_facts_for_different_survey_not_summed(self):
        "must discriminate by survey"
        # associate self.subject with self.survey
        self._save_fact('01', subject=self.subject, survey=self.survey)

        # associate self.subject2 with a different survey
        survey2 = Survey.objects.create(name='other', project=self.project)
        self._save_fact('01', subject=self.subject2, survey=survey2)

        subjects_qs = Project.objects\
                .filter(id__in=(self.subject.id, self.subject2.id))
        total = sum_facts_where(self.survey, subjects_qs,
                match_df=self.desired_fact, match_value=None,
                sum_dfs=self.desired_fact)

        self.assertEquals(1, total)

    def test_sum_facts_no_match(self):
        subjects_qs = Project.objects.none()
        self.assertEquals(0, sum_facts(self.survey, subjects_qs,
            self.desired_fact))

    def test_sum_facts(self):
        self._save_fact('01', subject=self.subject)
        self._save_fact('01', subject=self.subject2)

        subjects_qs = Project.objects\
                .filter(id__in=(self.subject.id, self.subject2.id))

        self.assertEquals(2, sum_facts(self.survey,
            subjects_qs, self.desired_fact))
