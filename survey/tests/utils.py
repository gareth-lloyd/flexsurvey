from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from survey.models import (Project, Survey, Fact,
        SurveyDesiredFact, DesiredFact, DesiredFactGroup)
from survey import forms

class SurveyTestCase(TestCase):
    def setUp(self):
        # any model instance will do for a subject at this time. We
        # create a project because it's already available.

        self.subject = Project.objects.create(name='subject_standin')
        self.content_type = ContentType.objects.get_for_model(self.subject)

        self.project = Project.objects.create(name='p')
        self.survey = Survey.objects.create(project=self.project,
                name='survey1')

        self.desired_fact = DesiredFact.objects.create(code='code1',
                label='enter data', data_type='T',
                required=True, content_type=self.content_type)
        self.fact_group = DesiredFactGroup.objects.create(heading='group1')
        SurveyDesiredFact.objects.create(survey=self.survey, 
                fact_group=self.fact_group, desired_fact=self.desired_fact)

    def _get_fact(self, data):
        return Fact.objects.get(desired_fact=self.desired_fact, data=data)

    def _save_fact(self, data, subject=None, survey=None, desired_fact=None,
                   user=None):
        subject = subject or self.subject
        survey = survey or self.survey
        desired_fact = desired_fact or self.desired_fact
        user = user or self.user
        return Fact.objects.create(survey=survey, subject=subject,
                                    desired_fact=desired_fact, data=data,
                                    created_by=user, updated_by=user)

    def _create_bound_form_with_field_type(self, data_type, data=None):
        self.desired_fact.data_type = data_type
        self.desired_fact.save()
        cls = forms.make_survey_form_subclass(self.survey, self.content_type)
        if data:
            return cls(self.survey, self.subject, self.user, data={'code1': data})
        else:
            return cls(self.survey, self.subject, self.user)

    def login(self):
        self.user = User(username='test')
        self.user.set_password('test')
        self.user.save()
        self.client.login(username='test', password='test')
