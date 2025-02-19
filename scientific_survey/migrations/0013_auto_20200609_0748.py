# Generated by Django 3.0.7 on 2020-06-09 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("scientific_survey", "0012_add_display_by_category")]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="type",
            field=models.CharField(
                choices=[
                    ("text", "text (multiple line)"),
                    ("short-text", "short text (one line)"),
                    ("radio", "radio"),
                    ("select", "select"),
                    ("select-multiple", "Select Multiple"),
                    ("select_image", "Select Image"),
                    ("integer", "integer"),
                    ("float", "float"),
                    ("date", "date"),
                ],
                default="text",
                max_length=200,
                verbose_name="Type",
            ),
        )
    ]
