# -*- coding: utf-8 -*-
import logging
from datetime import date, timedelta

from django.conf import settings
from django.shortcuts import Http404, redirect, render, reverse
from django.views.generic import View

from scientific_survey.decorators import survey_available
from scientific_survey.forms import ResponseForm

LOGGER = logging.getLogger(__name__)


class SurveyDetail(View):
    @survey_available
    def get(self, request, *args, **kwargs):
        survey = kwargs.pop("survey", None)
        step = kwargs.pop("step", 0)
        seed = kwargs.pop("seed", None)

        session_key = "survey_%s" % (kwargs["id"],)
        scope_cat = None
        if session_key in request.session:
            scope_cat = request.session[session_key].get("scope_cat", None)
        if survey.template is not None and len(survey.template) > 4:
            template_name = survey.template
        else:
            if survey.is_all_in_one_page():
                template_name = "scientific_survey/one_page_survey.html"
            else:
                template_name = "scientific_survey/survey.html"
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))

        if survey.categories_as_surveys and step == 0:
            cats2choose = survey.get_bookable_categories()
            if not cats2choose:
                raise Http404

        form = ResponseForm(
            survey=survey, user=request.user,
            step=step, seed=seed,
            scope=scope_cat,
            extra=request.GET.urlencode()
        )
        if form.scope_category_id:
            if session_key not in request.session:
                request.session[session_key] = {}
            request.session[session_key]["scope_cat"] = form.scope_category_id
            request.session.modified = True

        categories = form.current_categories()

        asset_context = {
            # If any of the widgets of the current form has a "date" class, flatpickr will be loaded into the template
            "flatpickr": any([field.widget.attrs.get("class") == "date" for _, field in form.fields.items()])
        }
        context = {
            "response_form": form,
            "survey": survey,
            "categories": categories,
            "step": step,
            "asset_context": asset_context,
        }

        return render(request, template_name, context)

    @survey_available
    def post(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))

        form = ResponseForm(
            request.POST,
            survey=survey,
            user=request.user,
            step=kwargs.get("step", 0),
            scope=request.POST.get("scope"),
            seed=request.POST.get("seed"),
            extra=request.POST.get("extra"),
        )
        categories = form.current_categories()

        if not survey.editable_answers and form.response is not None:
            LOGGER.info("Redirects to survey list after trying to edit non editable answer.")
            return redirect(reverse("survey-list"))
        context = {"response_form": form, "survey": survey, "categories": categories}
        if form.is_valid():
            return self.treat_valid_form(form, kwargs, request, survey)
        return self.handle_invalid_form(context, form, request, survey)

    @staticmethod
    def handle_invalid_form(context, form, request, survey):
        LOGGER.info("Non valid form: <%s>", form)
        if survey.template is not None and len(survey.template) > 4:
            template_name = survey.template
        else:
            if survey.is_all_in_one_page():
                template_name = "scientific_survey/one_page_survey.html"
            else:
                template_name = "scientific_survey/survey.html"
        return render(request, template_name, context)

    def final_redirect(self, survey, response):
        if survey.categories_as_surveys:
            cats2choose = survey.get_bookable_categories()
            if not cats2choose:
                survey.expire_date = date.today() - timedelta(days=1)
                survey.save()

        if survey.external_redirect:
            return redirect(survey.external_redirect)
        else:
            return redirect("survey-confirmation", uuid=response.interview_uuid)

    def treat_valid_form(self, form, kwargs, request, survey):
        session_key = "survey_%s" % (kwargs["id"],)
        if session_key not in request.session:
            request.session[session_key] = {}
        for key, value in list(form.cleaned_data.items()):
            request.session[session_key][key] = value
        request.session[session_key]["scope_cat"] = form.scope_category_id
        request.session.modified = True

        next_url = form.next_step_url()

        response = None
        if survey.is_all_in_one_page():
            response = form.save()
        else:
            # when it's the last step
            if form.has_next_step():
                request.session[session_key]["next_url"] = next_url
                request.session.modified = True
            else:
                save_form = ResponseForm(
                    request.session[session_key],
                    survey=survey,
                    user=request.user,
                    scope=request.session[session_key].get("scope_cat"),
                    seed=form.random_seed,
                    extra=form.extra,
                )
                if save_form.is_valid():
                    response = save_form.save()
                else:
                    LOGGER.warning("A step of the multipage form failed but should have been discovered before.")
                    LOGGER.error(save_form.errors)
        # if there is a next step
        if next_url is not None:
            return redirect(next_url)
        del request.session[session_key]

        if response is None:
            return redirect(reverse("survey-error"))

        next_ = request.session.get("next", None)
        if next_ is not None:
            if "next" in request.session:
                del request.session["next"]
            return redirect(next_)

        return self.final_redirect(survey, response)
