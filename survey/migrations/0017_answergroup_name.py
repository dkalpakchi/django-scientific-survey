# Generated by Django 3.1 on 2021-01-19 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0016_auto_20210119_0940"),
    ]

    operations = [
        migrations.AddField(
            model_name="answergroup",
            name="name",
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name="Name"),
        ),
    ]
