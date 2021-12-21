# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("scientific_survey", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="survey", name="template", field=models.CharField(max_length=255, null=True, blank=True)
        )
    ]
