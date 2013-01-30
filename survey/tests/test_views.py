from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from survey.models import DesiredFact, SurveyDesiredFact, Fact
from survey.tests.utils import SurveyTestCase
from survey.views import _update_fact

class UpdateFactTests(SurveyTestCase):

    def test_with_sdfs_for_multiple_content_types(self):
        "test to reproduce a bug encountered in actual use"
        user = User(username='test')
        user.set_password('test')
        user.save()

        content_type_2 = ContentType.objects.get_for_model(User)

        # another desired fact with same code, different content type
        desired_fact_2 = DesiredFact.objects.create(code=self.desired_fact.code,
                label='enter data', data_type='T',
                required=True, content_type=content_type_2)
        SurveyDesiredFact.objects.create(survey=self.survey, 
                fact_group=self.fact_group, desired_fact=desired_fact_2)

        _update_fact(self.survey, self.subject, self.desired_fact.code,
                self.content_type, data='01', user=user)

        self.assertTrue(Fact.objects.filter(survey=self.survey,
                        content_type=self.content_type,
                        object_id=self.subject.id).exists())
