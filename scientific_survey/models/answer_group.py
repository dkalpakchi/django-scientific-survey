# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .question import Question

LOGGER = logging.getLogger(__name__)


CHOICES_HELP_TEXT = _(
    """The choices field is only used if the question type
if the question type is 'radio', 'select',
'select multiple', or range. For the first 3, please provide
a comma-separated list of options for this question, for range,
please provide a comma-separated list of min,max,step."""
)


def validate_choices(choices):
    """Verifies that there is at least two choices in choices
    :param String choices: The string representing the user choices.
    """
    if settings.CHOICES_SEPARATOR in choices:
        values = choices.split(settings.CHOICES_SEPARATOR)
    else:
        # fallback to the default separator if new separator is not present
        values = choices.split(",")
    empty = 0
    for value in values:
        if value.replace(" ", "") == "":
            empty += 1
    if len(values) < 2 + empty:
        msg = "The selected field requires an associated list of choices."
        msg += " Choices must contain more than one item."
        raise ValidationError(msg)


class AnswerGroup(models.Model):
    TEXT = "text"
    SHORT_TEXT = "short-text"
    RADIO = "radio"
    SELECT = "select"
    SELECT_IMAGE = "select_image"
    SELECT_MULTIPLE = "select-multiple"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    INTEGER_RANGE = "range_int"
    FLOAT_RANGE = "range_float"

    QUESTION_TYPES = (
        (TEXT, _("text (multiple line)")),
        (SHORT_TEXT, _("short text (one line)")),
        (RADIO, _("radio")),
        (SELECT, _("select")),
        (SELECT_MULTIPLE, _("Select Multiple")),
        (SELECT_IMAGE, _("Select Image")),
        (INTEGER, _("integer")),
        (FLOAT, _("floating-point number")),
        (DATE, _("date")),
        (INTEGER_RANGE, _("range (integers)")),
        (FLOAT_RANGE, _("range (floating-point numbers)"))
    )

    type = models.CharField(_("Type"), max_length=200, choices=QUESTION_TYPES, default=TEXT)
    choices = models.TextField(_("Choices"), blank=True, null=True, help_text=CHOICES_HELP_TEXT)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name=_("Answer group"), related_name="answer_groups"
    )
    name = models.CharField(_("Name"), blank=True, max_length=300, null=True)
    prefix = models.CharField(_("Prefix"), blank=True, max_length=300, null=True)
    suffix = models.CharField(_("Suffix"), blank=True, max_length=300, null=True)

    def save(self, *args, **kwargs):
        if self.type in [AnswerGroup.RADIO, AnswerGroup.SELECT, AnswerGroup.SELECT_MULTIPLE]:
            validate_choices(self.choices)
        super(AnswerGroup, self).save(*args, **kwargs)

    def get_clean_choices(self):
        """ Return split and stripped list of choices with no null values. """
        if self.choices is None:
            return []
        choices_list = []
        for choice in self.choices.split(
            settings.CHOICES_SEPARATOR if settings.CHOICES_SEPARATOR in self.choices else ","
        ):
            choice = choice.strip()
            if choice:
                choices_list.append(choice)
        return choices_list

    def get_choices(self):
        """
        Parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.
        """
        choices_list = []
        for choice in self.get_clean_choices():
            choices_list.append((slugify(choice, allow_unicode=True), choice))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def __str__(self):
        return "{}: {}".format(self.name, self.get_clean_choices())
