from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.utils.datastructures import MultiValueDict

YES_CODE, NO_CODE = 1, 2
TEXT, SELECT, INT, FLOAT, YES_NO, MULTI = 'T', 'S', 'I', 'F', 'Y', 'M'
DATA_TYPES = (
    (TEXT, 'Free text'),
    (INT, 'Whole number'),
    (FLOAT, 'Number with a decimal points'),
    (YES_NO, 'Boolean, yes/no'),
    (SELECT, 'Selection from a list'),
    (MULTI, 'Multiple selections from a list'),
)

class Project(models.Model):
    """A project is an organizing category for multiple surveys.
    """
    name = models.CharField(max_length = 255)
    created_date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class Survey(models.Model):
    """A survey is a set of desired facts that will be gathered for
    a set of subjects.
    """
    project = models.ForeignKey(Project)
    name = models.CharField(max_length = 255)
    description = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    desired_facts = models.ManyToManyField('DesiredFact',
            through='SurveyDesiredFact')

    def content_types(self):
        """Get the content types for which this survey has defined
        questions
        """
        c_type_ids = DesiredFact.objects.filter(surveys=self)\
                .values_list('content_type', flat=True).distinct()
        return [ContentType.objects.get(id=c_type_id)
                for c_type_id in c_type_ids]

    @property
    def subject(self):
        try:
            SurveySubject.objects.get(survey=self, parent=None)
        except SurveySubject.MultipleObjectsReturned:
            raise ValueError("Multiple top-level SurveySubjects for this "\
                    "survey. This must be fixed before continuing.")

    def child_subjects(self, current_content_type):
        return SurveySubject.objects.filter(survey=self,
                 parent__content_type=current_content_type)

    def __unicode__(self):
        return self.name


class SurveySubject(models.Model):
    """Records the types of things that a particular survey is designed to
    interrogate. These things may be arranged in a hierarchy, I.e. a 'household'
    entity may contain several 'member' entities.
    """
    survey = models.ForeignKey(Project)
    parent = models.ForeignKey('survey.SurveySubject', blank=True, null=True)
    content_type = models.ForeignKey(ContentType)
    allow_multiple = models.BooleanField(default=True)


class DesiredFact(models.Model):
    """A description of a single piece of information that we hope to gather
    from subjects with a particular content_type.
    """
    code = models.CharField(max_length=512, db_index=True)
    label = models.CharField(max_length=1024)
    help_text = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType)

    data_type = models.CharField(max_length=2, choices=DATA_TYPES)
    minimum = models.IntegerField(blank=True, null=True)
    maximum = models.IntegerField(blank=True, null=True)
    required = models.BooleanField()

    surveys = models.ManyToManyField(Survey, through='SurveyDesiredFact')

    @property
    def choices(self):
        """Return a list of code, description tuples for choices. Format the
        description to make selection from drop-downs easier.
        """
        if self.data_type == YES_NO:
            cs = [(YES_CODE, '%s-Yes' % YES_CODE), (NO_CODE, '%s-No' % NO_CODE)]
        else:
            cs = [(fo.code, "%s-%s" % (fo.code.lstrip('0'), fo.description))
                for fo in self.factoption_set.all().order_by('code')]
        cs.insert(0, ('', 'Make a selection'))
        return cs

    def __unicode__(self):
        return self.label


class FactOption(models.Model):
    """Possible values that a particular desired fact can take.
    """
    desired_fact = models.ForeignKey(DesiredFact)
    code = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.description

    class Meta:
        unique_together = ('desired_fact', 'code')


class DesiredFactGroup(models.Model):
    """Some desired facts are grouped together under some heading.
    """
    heading = models.CharField(max_length = 255)
    # 'lighter' items come first in sequence
    weight = models.FloatField(default=1)

    def __unicode__(self):
        return self.heading


class SurveyDesiredFact(models.Model):
    """Embodies the relationship between surveys and desired facts: desired
    facts can belong to multiple surveys, and surveys can have many facts.
    """
    survey = models.ForeignKey(Survey)
    desired_fact = models.ForeignKey(DesiredFact)
    fact_group = models.ForeignKey(DesiredFactGroup)

    weight = models.FloatField(default=1)

    class Meta:
        # a desired fact can only appear once in each survey
        unique_together = ('survey', 'desired_fact')

    def __unicode__(self):
        return "{survey} > {fact_group} > {desired_fact}".format(survey=self.survey,
                desired_fact=self.desired_fact, fact_group=self.fact_group)


class Fact(models.Model):
    """A single piece of information gathered for one subject, in the course of
    a survey, and related to one desired fact.

    We store the data on this model. We could try to handle types of fact with
    polymorphism, e.g. having fact subtypes to handle references, text and numeric
    data. However this generally makes things harder to query and reason about.

    Munging all data into text and storing it here is not particularly pretty,
    but it works.
    """
    survey = models.ForeignKey(Survey)
    desired_fact = models.ForeignKey(DesiredFact)
    data = models.CharField(max_length=1024)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    subject = generic.GenericForeignKey('content_type', 'object_id')


    created_by = models.ForeignKey(User, related_name='created_by')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, related_name='updated_by')
    updated_on = models.DateTimeField(auto_now=True)

    @property
    def typed_data(self):
        _type = self.desired_fact.data_type
        if _type == TEXT:
            return self.data
        if _type == INT:
            return int(self.data or 0)
        if _type == FLOAT:
            return float(self.data or 0)
        if _type == YES_NO:
            return int(self.data) == YES_CODE
        if _type in (SELECT, MULTI):
            return FactOption.objects\
                    .get(desired_fact=self.desired_fact, code=self.data)

        raise ValueError("Desired fact %s has invalid data_type" % self)

    @staticmethod
    def create_or_update(survey, desired_fact, content_type, object_id, data,
                         user):
        if data is None:
            return
        elif isinstance(data, (list, tuple)):
            if desired_fact.data_type != MULTI:
                raise ValueError('Multiple fact instances for non-multi desired fact')
            current_data = Fact.objects.filter(survey=survey,
                    desired_fact=desired_fact, object_id=object_id,
                    content_type=content_type)\
                    .values_list('data', flat=True)
            current_data = set(current_data)
            incoming_data = set(data)
            for data_to_add in incoming_data - current_data:
                Fact.objects.create(survey=survey, data=data_to_add,
                        desired_fact=desired_fact, object_id=object_id,
                        content_type=content_type, created_by=user,
                        updated_by=user)
            for data_to_del in current_data - incoming_data:
                Fact.objects.filter(survey=survey, data=data_to_del,
                        desired_fact=desired_fact, object_id=object_id,
                        content_type=content_type).delete()
        else:
            try:
                fact, created = Fact.objects.get_or_create(survey=survey,
                        content_type=content_type, object_id=object_id,
                        desired_fact=desired_fact, defaults={'data': data,
                                                             'created_by': user,
                                                             'updated_by': user})
            except MultipleObjectsReturned:
                # delete all but the most recently created fact
                facts = list(Fact.objects.filter(survey=survey,
                        content_type=content_type, object_id=object_id,
                        desired_fact=desired_fact).order_by('created_on'))
                for fact in facts[:-1]:
                    fact.delete()
                fact, created = facts[-1], False

            if not created and fact.data != data:
                fact.data = data
                fact.updated_by = user
                fact.save()

    @staticmethod
    def existing_facts(survey, subject, prefix=None):
        """return all facts for a given survey and subject as a MultiValueDict,
        so that it can be bound to a form.
        """
        content_type = ContentType.objects.get_for_model(subject)
        facts = Fact.objects.filter(survey=survey,
                content_type=content_type, object_id=subject.id)\
                .select_related('desired_fact')

        fmt = (prefix and "%s-%s" % (prefix, "%s")) or "%s"
        existing_facts = MultiValueDict()
        for fact in facts:
            code = fmt % fact.desired_fact.code
            existing_facts.appendlist(code, fact.data)

        return existing_facts

    def __unicode__(self):
        return "{data} about {desired_fact} for {subject}".format(data=self.data,
                desired_fact=self.desired_fact, subject=self.subject)


def has_required_data(survey, subject):
    """True if this subject has facts present for all required
    facts in the supplied survey. Otherwise False.
    """
    content_type = ContentType.objects.get_for_model(subject)
    required_ids = DesiredFact.objects\
            .filter(surveys=survey, required=True, content_type=content_type)\
            .values_list('id', flat=True)
    present_ids = Fact.objects.filter(survey=survey,
            content_type=content_type, object_id=subject.id)\
            .values_list('desired_fact_id', flat=True)
    return not set(required_ids).difference(set(present_ids))


