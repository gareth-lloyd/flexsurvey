from django.conf.urls import patterns, url, include

from survey import views

urlpatterns = patterns('',
    url(r'^projects/$', views.ProjectsListView.as_view(),
        name='project-list'),

    url(r'^survey/(?P<pk>\d+)/$', views.SurveyDetailView.as_view(),
        name='survey-detail'),

    url(r'^survey/(?P<survey_id>\d+)/desiredfacts/$',
        views.DesiredFactListView.as_view(),
        name='survey-desired-facts'),

    url(r'^survey/(?P<survey_id>\d+)/ajaxfact/$',
        views.ajax_fact,
        name='survey-ajax-fact'),

    url(r'^survey/(?P<survey_id>\d+)/(?P<app>\w+)/(?P<model>\w+)/(?P<pk>\w+)/detail/$',
        views.SurveySubjectDetailView.as_view(), name='subject-detail'),

    url(r'^survey/(?P<survey_id>\d+)/(?P<app>\w+)/(?P<model>\w+)/(?P<subject_id>\w+)/edit/$',
        views.EditSurveySubjectView.as_view(), name='data-entry'),
)
