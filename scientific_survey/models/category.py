# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .survey import Survey


class Category(models.Model):

    name = models.CharField(_("Name"), max_length=400)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="categories")
    order = models.IntegerField(_("Display order"), blank=True, null=True)
    max_responses = models.IntegerField(_("Maximal number of responses"), default=1,
                                        help_text="Only applicable if categories are treated as separate sub-surveys")
    description = models.CharField(_("Description"), max_length=2000, blank=True, null=True)

    class Meta:
        # pylint: disable=too-few-public-methods
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return str(self.name)

    def slugify(self):
        return slugify(str(self))


class CategoryBooking(models.Model):
    """
    Keeps track of started surveys when categories are treated as independent surveys.
    This includes those cases, when the survey was taken, but not finished.
    The reason is that when a participant takes on a survey, we don't know ahead of time
    when it will be finished, which is why we simply keep the category booked.

    Instead of providing a default timeout and releasing the booking, we keep this process
    manual, acknowledging that sometimes a timeout might not at all be desirable.
    """
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE,
        verbose_name=_("Survey"), related_name="booked_categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        verbose_name=_("Category"), related_name="booked_in_surveys"
    )
    filled_slots = models.IntegerField(_("Number of booked slots"), default=1)
    dt_created = models.DateTimeField(null=True, default=timezone.now, verbose_name=_("Created at"),
                                      help_text=_("Autofilled"))
    dt_updated = models.DateTimeField(null=True, verbose_name=_("Updated at"),
                                      help_text=_("Autofilled"))
