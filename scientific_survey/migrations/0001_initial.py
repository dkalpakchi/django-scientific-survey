# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="AnswerBase",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("name", models.CharField(max_length=400)),
                ("order", models.IntegerField(null=True, blank=True)),
            ],
            options={"verbose_name": "category", "verbose_name_plural": "categories"},
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("text", models.TextField()),
                ("order", models.IntegerField()),
                ("required", models.BooleanField()),
                (
                    "question_type",
                    models.CharField(
                        default=b"text",
                        max_length=200,
                        choices=[
                            (b"text", "text (multiple line)"),
                            (b"short-text", "short text (one line)"),
                            (b"radio", "radio"),
                            (b"select", "select"),
                            (b"select-multiple", "Select Multiple"),
                            (b"select_image", "Select Image"),
                            (b"integer", "integer"),
                        ],
                    ),
                ),
                (
                    "choices",
                    models.TextField(
                        help_text=(
                            "if the question type is 'radio', 'select', or 'select multiple' provide a "
                            "comma-separated list of options for this question ."
                        ),
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True, to="scientific_survey.Category", null=True, on_delete=models.SET_NULL
                    ),
                ),
            ],
            options={"ordering": ("survey", "order"), "verbose_name": "question", "verbose_name_plural": "questions"},
        ),
        migrations.CreateModel(
            name="Response",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("interview_uuid", models.CharField(max_length=36, verbose_name="Interview unique identifier")),
            ],
            options={"verbose_name": "response", "verbose_name_plural": "responses"},
        ),
        migrations.CreateModel(
            name="Survey",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("name", models.CharField(max_length=400)),
                ("description", models.TextField()),
                ("is_published", models.BooleanField()),
                ("need_logged_user", models.BooleanField()),
                ("display_by_question", models.BooleanField()),
            ],
            options={"verbose_name": "survey", "verbose_name_plural": "surveys"},
        ),
        migrations.CreateModel(
            name="AnswerInteger",
            fields=[
                (
                    "answerbase_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="scientific_survey.AnswerBase",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("body", models.IntegerField(null=True, blank=True)),
            ],
            bases=("scientific_survey.answerbase",),
        ),
        migrations.CreateModel(
            name="AnswerRadio",
            fields=[
                (
                    "answerbase_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="scientific_survey.AnswerBase",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("body", models.TextField(null=True, blank=True)),
            ],
            bases=("scientific_survey.answerbase",),
        ),
        migrations.CreateModel(
            name="AnswerSelect",
            fields=[
                (
                    "answerbase_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="scientific_survey.AnswerBase",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("body", models.TextField(null=True, blank=True)),
            ],
            bases=("scientific_survey.answerbase",),
        ),
        migrations.CreateModel(
            name="AnswerSelectMultiple",
            fields=[
                (
                    "answerbase_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="scientific_survey.AnswerBase",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("body", models.TextField(null=True, blank=True)),
            ],
            bases=("scientific_survey.answerbase",),
        ),
        migrations.CreateModel(
            name="AnswerText",
            fields=[
                (
                    "answerbase_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="scientific_survey.AnswerBase",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("body", models.TextField(null=True, blank=True)),
            ],
            bases=("scientific_survey.answerbase",),
        ),
        migrations.AddField(
            model_name="response",
            name="survey",
            field=models.ForeignKey(to="scientific_survey.Survey", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="response",
            name="user",
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name="question",
            name="survey",
            field=models.ForeignKey(to="scientific_survey.Survey", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="category",
            name="survey",
            field=models.ForeignKey(to="scientific_survey.Survey", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="answerbase",
            name="question",
            field=models.ForeignKey(to="scientific_survey.Question", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="answerbase",
            name="response",
            field=models.ForeignKey(to="scientific_survey.Response", on_delete=models.CASCADE),
        ),
    ]
