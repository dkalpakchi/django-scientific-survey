# -*- coding: utf-8 -*-

from django.conf.urls import url

from scientific_survey.views import ConfirmView, IndexView, SurveyCompleted, SurveyDetail, survey_error, survey_full
from scientific_survey.views.import_view import import_from_yaml

urlpatterns = [
    url(r"^$", IndexView.as_view(), name="survey-list"),
    url(r"^error", survey_error, name="survey-error"),
    url(r"^full", survey_full, name="survey-full"),
    url(r"^(?P<id>\d+)/", SurveyDetail.as_view(), name="survey-detail"),
    url(r"^(?P<id>\d+)/completed/", SurveyCompleted.as_view(), name="survey-completed"),
    url(r"^(?P<id>\d+)-(?P<step>\d+)-(?P<seed>\d+)/", SurveyDetail.as_view(), name="survey-detail-step"),
    url(r"^confirm/(?P<uuid>\w+)/", ConfirmView.as_view(), name="survey-confirmation"),
    url(r"^import/yaml", import_from_yaml, name="survey-import-from-yaml"),
]
