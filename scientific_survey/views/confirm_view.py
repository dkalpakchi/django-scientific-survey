# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.views.generic import TemplateView

from scientific_survey.models import Response


class ConfirmView(TemplateView):

    template_name = "scientific_survey/confirm.html"

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        context["uuid"] = str(kwargs["uuid"])
        context["response"] = Response.objects.get(interview_uuid=context["uuid"])

        if context["response"].survey.categories_as_surveys:
            cats2choose = context["response"].survey.get_bookable_categories()
            if not cats2choose:
                context["response"].survey.expire_date = date.today() - timedelta(days=1)
                context["response"].survey.save()
        return context
