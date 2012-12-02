from collections import OrderedDict, defaultdict

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.util import ErrorDict
from form_utils.forms import BetterForm

from survey import models


class FactField(forms.Field):
    FACT_FIELD_CLASS = 'factFormField'
    html_class = 'text'

    def __init__(self, desired_fact, *args, **kwargs):
        self.desired_fact = desired_fact
        kwargs.update(
            required=desired_fact.required,
            label=desired_fact.label,
            help_text=desired_fact.help_text)
        super(FactField, self).__init__(*args, **kwargs)

    def prep_data_for_saving(self, data):
        if data == '':
            return None
        return data

    def widget_attrs(self, widget_instance):
        "returns a dictionary of HTML attrs that should be added to the Widget"
        class_str = "%s %s" % (self.html_class, self.FACT_FIELD_CLASS)
        return {'class': class_str}


class TextFactField(FactField, forms.CharField):
    def __init__(self, desired_fact, *args, **kwargs):
        kwargs.update(max_length=desired_fact.maximum,
                min_length=desired_fact.minimum)
        super(TextFactField, self)\
                .__init__(desired_fact, *args, **kwargs)


class IntegerFactField(FactField, forms.IntegerField):
    html_class = 'integer'

    def __init__(self, desired_fact, *args, **kwargs):
        kwargs.update(max_value=desired_fact.maximum,
                min_value=desired_fact.minimum)
        super(IntegerFactField, self)\
                .__init__(desired_fact, *args, **kwargs)

    def prep_data_for_saving(self, data):
        if data is None or data == '':
            return None
        return str(data)


class FloatFactField(FactField, forms.FloatField):
    html_class = 'float'

    def __init__(self, desired_fact, *args, **kwargs):
        kwargs.update(max_value=desired_fact.maximum,
                min_value=desired_fact.minimum)
        super(FloatFactField, self)\
                .__init__(desired_fact, *args, **kwargs)

    def prep_data_for_saving(self, data):
        if data is None or data == '':
            return None
        return str(data)

class ChoiceFactField(FactField, forms.ChoiceField):
    html_class = 'select'

    def __init__(self, desired_fact, *args, **kwargs):
        kwargs.update(widget=forms.Select)
        super(ChoiceFactField, self)\
                .__init__(desired_fact, *args, **kwargs)
        self._set_choices(desired_fact.choices)


class MultipleChoiceFactField(FactField, forms.MultipleChoiceField):
    html_class = 'multi-select'

    def __init__(self, desired_fact, *args, **kwargs):
        kwargs.update(widget=forms.SelectMultiple)
        super(MultipleChoiceFactField, self)\
                .__init__(desired_fact, *args, **kwargs)
        self._set_choices(desired_fact.choices)

    def prep_data_for_saving(self, data):
        return data


def fact_field_factory(desired_fact):
    classes = {
        models.MULTI: MultipleChoiceFactField,
        models.SELECT: ChoiceFactField,
        models.INT: IntegerFactField,
        models.FLOAT: FloatFactField,
        models.YES_NO: ChoiceFactField,
        models.TEXT: TextFactField,
    }
    cls = classes.get(desired_fact.data_type, FactField)
    return cls(desired_fact)


class BaseSurveyForm(BetterForm):
    def __init__(self, survey, subject, user, *args, **kwargs):
        self.survey, self.subject, self.user = survey, subject, user
        super(BaseSurveyForm, self).__init__(*args, **kwargs)

    def full_clean(self):
        """Override the django implementation - we don't want to delete the
        cleaned_data if the form is not valid.
        """
        self._errors = ErrorDict()
        if not self.is_bound: # Stop further processing.
            return
        self.cleaned_data = {}
        self._clean_fields()
        self._clean_form()
        self._post_clean()

    def save_valid(self):
        """Write any valid facts to the database.
        """
        content_type = ContentType.objects.get_for_model(self.subject)

        all_field_names = set(self.fields.keys())
        error_field_names = set(self.errors.keys())
        for field_name in all_field_names - error_field_names:
            data = self.cleaned_data.get(field_name)
            field = self.fields[field_name]
            data = field.prep_data_for_saving(data)
            self.create_fact(data, field.desired_fact, content_type)

    def create_fact(self, data, desired_fact, content_type):
        models.Fact.create_or_update(self.survey, desired_fact, content_type,
                self.subject.id, data, self.user)


def _survey_form_subclass(base_class, survey_desired_facts):
    """The desired facts for the survey are examined and used to
    create relevant form fields. We also generate configuration for
    the form's fieldsets according to the groupings defined in the
    relevant DesiredFactGroup instances.
    """
    form_attrs = OrderedDict()
    dfs_by_fact_group = defaultdict(list)
    fieldsets = []

    for sdf in survey_desired_facts:
        field = fact_field_factory(sdf.desired_fact)
        form_attrs[sdf.desired_fact.code] = field
        dfs_by_fact_group[sdf.fact_group].append(sdf.desired_fact)

    for fact_group, desired_facts in dfs_by_fact_group.iteritems():
        fieldset_opts = {
            'fields': [df.code for df in desired_facts],
            'legend': fact_group.heading,
        }
        fieldsets.append((fact_group.id, fieldset_opts))

    class Meta:
        pass
    Meta.fieldsets = fieldsets

    form_attrs.update(Meta=Meta)
    return type('SurveyForm', (base_class,), form_attrs)

def make_survey_form_subclass(survey, content_type):
    sdfs = models.SurveyDesiredFact.objects\
            .filter(survey=survey, desired_fact__content_type=content_type)\
            .select_related('fact_group', 'desired_fact')\
            .order_by('fact_group__weight', 'weight', 'desired_fact__code')
    return _survey_form_subclass(BaseSurveyForm, sdfs)
