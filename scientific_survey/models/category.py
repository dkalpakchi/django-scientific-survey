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
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE,
        verbose_name=_("Survey"), related_name="booked_categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        verbose_name=_("Category"), related_name="booked_in_surveys"
    )
    is_active = models.BooleanField(_("Is active?"), default=True)
    dt_created = models.DateTimeField(null=True, default=timezone.now, verbose_name=_("Created at"),
                                      help_text=_("Autofilled"))
    dt_updated = models.DateTimeField(null=True, verbose_name=_("Updated at"),
                                      help_text=_("Autofilled"))
