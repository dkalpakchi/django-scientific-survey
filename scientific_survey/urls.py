# -*- coding: utf-8 -*-

from django.conf.urls import url

from scientific_survey.views import ConfirmView, IndexView, SurveyCompleted, SurveyDetail
from scientific_survey.views.import_view import import_from_json

urlpatterns = [
    url(r"^$", IndexView.as_view(), name="survey-list"),
    url(r"^(?P<id>\d+)/", SurveyDetail.as_view(), name="survey-detail"),
    url(r"^(?P<id>\d+)/completed/", SurveyCompleted.as_view(), name="survey-completed"),
    url(r"^(?P<id>\d+)-(?P<step>\d+)-(?P<seed>\d+)/", SurveyDetail.as_view(), name="survey-detail-step"),
    url(r"^confirm/(?P<uuid>\w+)/", ConfirmView.as_view(), name="survey-confirmation"),
    url(r"^import/json", import_from_json, name="survey-import-from-json"),
]
