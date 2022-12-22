# -*- coding: utf-8 -*-

import nested_admin
from django.contrib import admin

from scientific_survey.actions import make_published
from scientific_survey.exporter.json import Survey2Json
from scientific_survey.models import Answer, AnswerGroup, Category, CategoryBooking, Layout, Question, Response, Survey


class AnswerGroupInline(nested_admin.NestedStackedInline):
    model = AnswerGroup
    extra = 0


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    ordering = ("order", "category")
    inlines = [AnswerGroupInline]
    extra = 1

    def get_formset(self, request, survey_obj, *args, **kwargs):
        formset = super(QuestionInline, self).get_formset(request, survey_obj, *args, **kwargs)
        if survey_obj:
            formset.form.base_fields["category"].queryset = survey_obj.categories.all()
        return formset


class CategoryInline(nested_admin.NestedTabularInline):
    model = Category
    extra = 0


class SurveyAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "is_published", "need_logged_user", "template")
    list_filter = ("is_published", "need_logged_user")
    inlines = [CategoryInline, QuestionInline]
    actions = [make_published, Survey2Json.export_as_json]  # Survey2Csv.export_as_csv, Survey2Tex.export_as_tex,


class AnswerBaseInline(admin.StackedInline):
    fields = ("question", "question_category", "answer_group", "body")
    readonly_fields = ("question", "answer_group", "question_category")
    extra = 0
    model = Answer


class ResponseAdmin(admin.ModelAdmin):
    list_display = ("interview_uuid", "survey", "created", "user")
    list_filter = ("survey", "created")
    date_hierarchy = "created"
    inlines = [AnswerBaseInline]
    # specifies the order as well as which fields to act on
    readonly_fields = ("survey", "created", "updated", "interview_uuid", "user")


class CategoryBookingAdmin(admin.ModelAdmin):
    # specifies the order as well as which fields to act on
    raw_id_fields = ("survey", "category")
    list_display = ("survey", "category", "filled_slots")


class LayoutAdmin(admin.ModelAdmin):
    # specifies the order as well as which fields to act on
    list_display = ("codename", "owner")


# admin.site.register(Question, QuestionInline)
# admin.site.register(Category, CategoryInline)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(CategoryBooking, CategoryBookingAdmin)
admin.site.register(Layout, LayoutAdmin)
