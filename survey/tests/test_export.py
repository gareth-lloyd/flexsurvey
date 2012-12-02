from survey.tests.utils import SurveyTestCase
from survey.models import Fact, Project
from survey.export import export_subject, export_subjects

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

