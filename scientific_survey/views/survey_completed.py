# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from scientific_survey.models import Survey


class SurveyCompleted(TemplateView):

    template_name = "scientific_survey/completed.html"

    def get_context_data(self, **kwargs):
        context = {}
        survey = get_object_or_404(Survey, is_published=True, id=kwargs["id"])
        context["survey"] = survey
        return context
