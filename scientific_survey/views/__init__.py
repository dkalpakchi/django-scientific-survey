# -*- coding: utf-8 -*-

from scientific_survey.views.confirm_view import ConfirmView
from scientific_survey.views.index_view import IndexView
from scientific_survey.views.survey_completed import SurveyCompleted
from scientific_survey.views.survey_detail import SurveyDetail
from scientific_survey.views.util_views import survey_error, survey_full

__all__ = ["SurveyCompleted", "IndexView", "ConfirmView", "SurveyDetail", "survey_full", "survey_error"]
