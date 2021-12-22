from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ScientificSurveyConfig(AppConfig):

    """
    See https://docs.djangoproject.com/en/2.1/ref/applications/#django.apps.AppConfig
    """

    name = "scientific_survey"
    verbose_name = _("Scientific survey")
