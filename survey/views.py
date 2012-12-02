import json
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator

from survey import models, forms

class ProjectsListView(ListView):
    model = models.Project
    context_object_name = 'projects'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectsListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # TODO: only show logged in user's projects
        return models.Project.objects.filter()


class SurveyDetailView(DetailView):
    context_object_name = 'survey'
    model = models.Survey

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SurveyDetailView, self).dispatch(request, *args, **kwargs)


class DesiredFactListView(ListView):
    model = models.DesiredFact
    context_object_name = 'desired_facts'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(models.Survey, pk=kwargs['survey_id'])
        return super(DesiredFactListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return models.DesiredFact.objects.filter(surveys=self.survey)

    def get_context_data(self, **kwargs):
        context = super(DesiredFactListView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        return context


class SurveySubjectDetailView(DetailView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(models.Survey, pk=kwargs['survey_id'])
        app_label, model_name = kwargs['app'], kwargs['model']
        self.content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
        return super(SurveySubjectDetailView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.content_type.model_class().objects.all()

    def get_context_object_name(self, obj):
        return self.content_type.name

    def get_template_names(self):
        return ['survey/%s_detail.html' % self.content_type.name,
                'survey/survey_subject_detail.html']

    def get_context_data(self, **kwargs):
        context = super(SurveySubjectDetailView, self).get_context_data(**kwargs)
        context['content_type'] = self.content_type
        context['survey'] = self.survey
        return context


class EditSurveySubjectView(FormView):
    """The view for creating survey forms form for subjects (when called via
    GET) or saving data about subjects (when called via POST). Implemented
    as a class-based view so that any aspect of its behaviour can be over-
    ridden and customized.
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(models.Survey, pk=kwargs['survey_id'])
        app_label, model_name = kwargs['app'], kwargs['model']
        self.content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
        self.subject = self.content_type.get_object_for_this_type(id=kwargs['subject_id'])

        return super(EditSurveySubjectView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return forms.make_survey_form_subclass(self.survey, self.content_type)

    def get_form_kwargs(self):
        kwargs = super(EditSurveySubjectView, self).get_form_kwargs()
        # we never want to set 'initial data:
        kwargs.pop('initial', None)

        kwargs.update(subject=self.subject, survey=self.survey, user=self.request.user)
        if self.request.method == 'GET':
            existing_facts = models.Fact.existing_facts(self.survey, self.subject)
            if existing_facts:
                kwargs.update(data=existing_facts)
        return kwargs

    def get_form(self, form_class):
        form = form_class(**self.get_form_kwargs())
        if self.request.method in ('POST', 'PUT'):
            form.save_valid()
        return form

    def form_valid(self, form):
        if models.has_required_data(self.survey, self.subject):
            redirect_url = reverse('survey-detail', kwargs={'pk': self.survey.id})
            return HttpResponseRedirect(redirect_url)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        #Detect if save button has been pressed rather than submit
        if 'Save' in self.request.POST:
            redirect_url = reverse('survey-detail', kwargs={'pk': self.survey.id})
            return HttpResponseRedirect(redirect_url)
        else:
            return super(EditSurveySubjectView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context_data = super(EditSurveySubjectView, self).get_context_data(**kwargs)
        context_data.update(survey=self.survey, subject=self.subject,
                            content_type=self.content_type)
        return context_data

    def get_template_names(self):
        """Allow the option of survey forms customized for particular
        content types. Fall back to a default survey form."""
        return ['survey/edit_survey_%s.html' % self.content_type.name,
                "survey/edit_survey_subject.html"]

@login_required
def ajax_fact(request, survey_id):
    survey = get_object_or_404(models.Survey, pk=survey_id)

    content_type_id = request.POST.get('contentTypeId')
    content_type = get_object_or_404(ContentType, pk=content_type_id)

    object_id = request.POST.get('objectId')
    subject = content_type.get_object_for_this_type(pk=object_id)

    code = request.POST.get('code')
    data = {code: request.POST.get('data')}

    # create a miniature form for this desired fact only, and save the fact
    sdfs = models.SurveyDesiredFact.objects\
            .filter(survey=survey, desired_fact__code=code)
    form_class = forms._survey_form_subclass(forms.BaseSurveyForm, sdfs)
    form = form_class(subject=subject, survey=survey, user=request.user, data=data)
    form.save_valid()

    return HttpResponse(json.dumps({'success': True}),
                        content_type="application/json")

