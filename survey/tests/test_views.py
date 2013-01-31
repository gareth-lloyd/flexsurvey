from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from survey.models import DesiredFact, SurveyDesiredFact
from survey.tests.utils import SurveyTestCase
from survey.views import _update_fact
from survey.forms import MultipleChoiceFactField

class UpdateFactTests(SurveyTestCase):

    def test_with_sdfs_for_multiple_content_types(self):
        "test to reproduce a bug encountered in actual use"
        user = User(username='test')
        user.set_password('test')
        user.save()

        content_type_2 = ContentType.objects.get_for_model(User)

        # another desired fact with same code, different content type, data type
        desired_fact_2 = DesiredFact.objects.create(code=self.desired_fact.code,
                label='enter data', data_type='M',
                required=True, content_type=content_type_2)
        SurveyDesiredFact.objects.create(survey=self.survey, 
                fact_group=self.fact_group, desired_fact=desired_fact_2)

        data = {self.desired_fact.code: '01'}
        form = _update_fact(self.survey, self.subject, desired_fact_2.code,
                content_type_2, data=data, user=user)

        # fail unless form was created from the correct SDF:
        self.assertTrue(isinstance(form.fields[desired_fact_2.code], 
            MultipleChoiceFactField))

