from django.forms import ValidationError
from django.utils.datastructures import MultiValueDict

from survey import forms
from survey.tests.utils import SurveyTestCase
from survey.models import Fact, FactOption


class FactFormTests(SurveyTestCase):
    def setUp(self):
        super(FactFormTests, self).setUp()
        self.login()

    def test_create_fact_from_form(self):
        cls = forms.make_survey_form_subclass(self.survey, self.content_type)
        form = cls(self.survey, self.subject, self.user, data={'code1': 'a'})
        form.save_valid()
        self.assertEquals(self.subject, Fact.objects.get(data='a').subject)

    def test_required_facts(self):
        form_class = forms.make_survey_form_subclass(self.survey, self.content_type)
        form = form_class(self.survey, self.subject, self.user, data={})
        self.assertFalse(form.is_valid())

    def test_non_required_facts(self):
        self.desired_fact.required = False
        self.desired_fact.save()
        form_class = forms.make_survey_form_subclass(self.survey, self.content_type)
        self.assertTrue(form_class(self.survey, self.subject, self.user, data={}).is_valid())

    def test_will_not_create_unspecified_facts(self):
        self.desired_fact.required = False
        self.desired_fact.save()

        form_class = forms.make_survey_form_subclass(self.survey, self.content_type)
        form_class(self.survey, self.subject, self.user, data={'code1': ''}).save_valid()
        self.assertFalse(Fact.objects.filter(
            desired_fact=self.desired_fact).exists())

    def test_save_valid_multiple_choice(self):
        self.desired_fact.data_type = 'M'
        self.desired_fact.save()

        FactOption.objects.create(desired_fact=self.desired_fact,
                code='01', description='1')
        FactOption.objects.create(desired_fact=self.desired_fact,
                code='02', description='2')

        cls = forms.make_survey_form_subclass(self.survey, self.content_type)
        post_data = MultiValueDict()
        post_data.appendlist('code1', '01')
        post_data.appendlist('code1', '02')
        cls(self.survey, self.subject, self.user, data=post_data).save_valid()

        self.assertTrue(Fact.objects.filter(
            desired_fact=self.desired_fact, data='01').exists())
        self.assertTrue(Fact.objects.filter(
            desired_fact=self.desired_fact, data='02').exists())


class FactFieldDataTypeTests(SurveyTestCase):

    def setUp(self):
        super(FactFieldDataTypeTests, self).setUp()
        self.login()

    def _set_min_max(self, min, max):

        self.desired_fact.minimum = min
        self.desired_fact.maximum = max
        self.desired_fact.save()

    def test_text_field(self):
        form = self._create_bound_form_with_field_type('T', 'hi')
        self.assertTrue(form.is_valid())

    def test_text_field_min_max_valid(self):
        self._set_min_max(0, 4)
        form = self._create_bound_form_with_field_type('T', 'hi')
        self.assertTrue(form.is_valid())

    def test_text_field_min_max_invalid(self):
        self._set_min_max(2, 4)
        form = self._create_bound_form_with_field_type('T', 'i')
        self.assertFalse(form.is_valid())

        form = self._create_bound_form_with_field_type('T', 'illicit')
        self.assertFalse(form.is_valid())

    def test_text_field_min_max_exact(self):
        "Test the case where an exact length is required"
        self._set_min_max(4, 4)
        form = self._create_bound_form_with_field_type('T', 'illi')
        self.assertTrue(form.is_valid())

        form = self._create_bound_form_with_field_type('T', 'illic')
        self.assertFalse(form.is_valid())

    def test_int_field(self):
        form = self._create_bound_form_with_field_type('I', '3')
        self.assertTrue(form.is_valid())
        form = self._create_bound_form_with_field_type('I', 'a')
        self.assertFalse(form.is_valid())

    def test_int_field_min_max(self):
        self._set_min_max(0, 3)
        form = self._create_bound_form_with_field_type('I', '3')
        self.assertTrue(form.is_valid())
        form = self._create_bound_form_with_field_type('I', '4')
        self.assertFalse(form.is_valid())

    def test_float_field(self):
        form = self._create_bound_form_with_field_type('F', '3.5')
        self.assertTrue(form.is_valid())
        form = self._create_bound_form_with_field_type('F', '3')
        self.assertTrue(form.is_valid())
        form = self._create_bound_form_with_field_type('F', 'a')
        self.assertFalse(form.is_valid())

    def test_float_field_min_max(self):
        self._set_min_max(0, 3)
        form = self._create_bound_form_with_field_type('F', '3')
        self.assertTrue(form.is_valid())
        form = self._create_bound_form_with_field_type('F', '4')
        self.assertFalse(form.is_valid())

    def test_yes_no_field(self):
        form = self._create_bound_form_with_field_type('Y', '1')
        self.assertTrue(form.is_valid())
        form = self._create_bound_form_with_field_type('Y', '4')
        self.assertFalse(form.is_valid())


class MultiSelectFactFieldTests(SurveyTestCase):
    def setUp(self):
        super(MultiSelectFactFieldTests, self).setUp()
        self.fact_option_1 = FactOption.objects.create(
                code='01', description='01', desired_fact=self.desired_fact)
        self.fact_option_2 = FactOption.objects.create(
                code='02', description='02', desired_fact=self.desired_fact)
        self.field = forms.MultipleChoiceFactField(self.desired_fact)
        self.login()

    def test_valid_none_required(self):
        self.assertRaises(ValidationError, self.field.clean, None)
        self.assertRaises(ValidationError, self.field.clean, '')

    def test_valid_none_not_required(self):
        self.desired_fact.required = False
        self.desired_fact.save()
        self.field = forms.MultipleChoiceFactField(self.desired_fact)
        self.assertEquals([], self.field.clean(None))
        self.assertEquals([], self.field.clean(''))

    def test_valid_str(self):
        self.assertRaises(ValidationError, self.field.clean, 'a')
        # invalid even if string is one of the correct options
        self.assertRaises(ValidationError, self.field.clean, '01')

    def test_valid(self):
        self.assertEquals(['01'], self.field.clean(['01']))
        self.assertEquals(['01', '02'], self.field.clean(['01', '02']))

    def test_create_fact(self):
        form = self._create_bound_form_with_field_type('M')
        form.create_fact(['01'], self.desired_fact, self.content_type)
        self.assertTrue(self._get_fact('01') is not None)

    def test_create_again(self):
        "subsequent calls with same data should not create more facts"
        form = self._create_bound_form_with_field_type('M')
        form.create_fact(['01'], self.desired_fact, self.content_type)
        form.create_fact(['01'], self.desired_fact, self.content_type)
        self.assertEquals(1, Fact.objects\
                .filter(desired_fact=self.desired_fact).count())

    def test_create_additional_fact(self):
        "Subsequent calls with differing data should create more facts"
        form = self._create_bound_form_with_field_type('M')
        form.create_fact(['01'], self.desired_fact, self.content_type)
        form.create_fact(['01', '02'], self.desired_fact, self.content_type)
        self.assertEquals(2, Fact.objects.filter(desired_fact=self.desired_fact)\
                .filter(data__in=['01', '02']).count())

    def test_change_selection(self):
        "Removing a selection should delete that data"
        form = self._create_bound_form_with_field_type('M')
        form.create_fact(['01'], self.desired_fact, self.content_type)
        form.create_fact(['02'], self.desired_fact, self.content_type)
        self.assertFalse(Fact.objects.filter(desired_fact=self.desired_fact)\
                .filter(data='01').exists())
        self.assertTrue(Fact.objects.filter(desired_fact=self.desired_fact)\
                .filter(data='02').exists())
