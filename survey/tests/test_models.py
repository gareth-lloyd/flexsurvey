from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from survey.tests.utils import SurveyTestCase
from survey.models import (DesiredFact, FactOption,
        Fact, has_required_data, Project)


class DesiredFactTests(TestCase):
    def setUp(self):
        self.content_type = ContentType.objects.all()[0]
        self.desired_fact = DesiredFact.objects.create(code='code1',
                label='enter data', data_type='T',
                required=True, content_type=self.content_type)

    def test_choices(self):
        FactOption.objects.create(code='1', description='a', 
                desired_fact=self.desired_fact)
        FactOption.objects.create(code='2', description='b', 
                desired_fact=self.desired_fact)

        self.assertEquals([('1', '1-a'), ('2', '2-b')],
                self.desired_fact.choices[1:])

class FactTests(SurveyTestCase):
    def setUp(self):
        super(FactTests, self).setUp()
        self.login()
    
    def _set_desired_fact_data_type(self, _type):
        self.desired_fact.data_type = _type
        self.desired_fact.save()

    def test_data_type_text(self):
        data = 'hi there'
        self._set_desired_fact_data_type('T')
        fact = self._save_fact(data)
        self.assertEquals(data, fact.typed_data)

    def test_data_type_int(self):
        data = '12'
        self._set_desired_fact_data_type('I')
        fact = self._save_fact(data)
        self.assertEquals(12, fact.typed_data)

    def test_data_type_float(self):
        data = '12.2'
        self._set_desired_fact_data_type('F')
        fact = self._save_fact(data)
        self.assertEquals(12.2, fact.typed_data)

    def test_data_type_yes_no(self):
        data = '01'
        self._set_desired_fact_data_type('Y')
        fact = self._save_fact(data)
        self.assertEquals(True, fact.typed_data)

    def test_data_type_select(self):
        fo = FactOption.objects.create(desired_fact=self.desired_fact, code='12')
        data = '12'
        self._set_desired_fact_data_type('S')
        fact = self._save_fact(data)
        self.assertEquals(fo, fact.typed_data)

    def test_existing_facts(self):
        self._save_fact('01')
        existing_facts = dict(Fact.existing_facts(self.survey, self.subject).items())
        self.assertEquals({'code1': '01'}, existing_facts)

    def test_existing_facts_with_prefix(self):
        self._save_fact('01')
        existing_facts = dict(Fact.existing_facts(
            self.survey, self.subject, 'prefix').items())
        self.assertEquals({'prefix-code1': '01'}, existing_facts)

class SubjectTests(SurveyTestCase):
    def setUp(self):
        super(SubjectTests, self).setUp()
        self.login()

    def test_survey_with_no_desired_facts(self):
        self.desired_fact.delete()
        self.assertTrue(has_required_data(self.survey, self.subject))

    def test_survey_with_non_required_data(self):
        self.desired_fact.required = False
        self.desired_fact.save()
        self.assertTrue(has_required_data(self.survey, self.subject))

    def test_survey_with_required_data(self):
        self.assertFalse(has_required_data(self.survey, self.subject))

        Fact.objects.create(survey=self.survey, subject=self.subject,
                desired_fact=self.desired_fact, data='1', created_by=self.user,
                updated_by=self.user)

        self.assertTrue(has_required_data(self.survey, self.subject))

    def test_survey_with_mixed_data(self):
        DesiredFact.objects.create(code='code2',
                label='enter data', data_type='T',
                required=False, content_type=self.content_type)
        self.assertFalse(has_required_data(self.survey, self.subject))

        Fact.objects.create(survey=self.survey, subject=self.subject,
                desired_fact=self.desired_fact, data='1', created_by=self.user,
                updated_by=self.user)

        self.assertTrue(has_required_data(self.survey, self.subject))

class SurveyTests(SurveyTestCase):

    def test_survey_content_types(self):
        self.assertEquals(
                [ContentType.objects.get_for_model(Project)],
                self.survey.content_types())
