# -*- coding: utf-8 -*-

import os
from pathlib import Path

from django.conf import settings

# Number of messages to display per page.
MESSAGES_PER_PAGE = getattr(settings, "ROSETTA_MESSAGES_PER_PAGE", 10)


ROOT = os.path.dirname(os.path.abspath(__file__))
USER_DID_NOT_ANSWER = getattr(settings, "USER_DID_NOT_ANSWER", "Left blank")
CHOICES_SEPARATOR = getattr(settings, "CHOICES_SEPARATOR", ",")
DEFAULT_SURVEY_PUBLISHING_DURATION = 7

MEDIA_URL = "/media/"
STATIC_URL = "/static/"

MEDIA_ROOT = Path(ROOT, "media")
STATIC_ROOT = Path(ROOT, "static")

DEBUG_ADMIN_NAME = "test_admin"
DEBUG_ADMIN_PASSWORD = "test_password"

STATICFILES_DIRS = [os.path.normpath(Path(ROOT, "..", "scientific_survey", "static"))]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(ROOT, "scientific_survey", "templates"), Path(ROOT, "dev", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Default
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


INSTALLED_APPS = ("scientific_survey", "bootstrapform")

LOCALE_PATHS = (Path(ROOT, "scientific_survey", "locale"),)
LANGUAGE_CODE = "en"
LANGUAGES = (
    ("en", "english"),
    ("ru-RU", "русский"),
    ("es", "spanish"),
    ("fr", "french"),
    ("ja", "Japanese"),
    ("zh", "Chinese"),
    ("de", "German"),
)
