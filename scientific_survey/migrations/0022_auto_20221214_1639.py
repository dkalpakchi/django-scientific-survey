# Generated by Django 3.2.16 on 2022-12-14 16:39

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scientific_survey', '0021_auto_20210210_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='responses', to='scientific_survey.category',
                                    verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='survey',
            name='categories_as_surveys',
            field=models.BooleanField(
                default=False,
                verbose_name='Use each category separately as an independent sub-survey'
            ),
        ),
        migrations.AddField(
            model_name='survey',
            name='save_categories_separately',
            field=models.BooleanField(
                default=False,
                verbose_name='Save data for each category in an independent response \
                        (only if categories are treated as sub-surveys)'
            ),
        ),
        migrations.AlterField(
            model_name='answergroup',
            name='choices',
            field=models.TextField(
                blank=True,
                help_text="The choices field is only used if the question type\n\
                        if the question type is 'radio', 'select',\n'select multiple', or range.\
                        For the first 3, please provide\na comma-separated list of options for \
                        this question, for range,\nplease provide a comma-separated \
                        list of min,max,step.",
                null=True,
                verbose_name='Choices'
            ),
        ),
        migrations.AlterField(
            model_name='answergroup',
            name='type',
            field=models.CharField(
                choices=[
                    ('text', 'text (multiple line)'),
                    ('short-text', 'short text (one line)'),
                    ('radio', 'radio'),
                    ('select', 'select'),
                    ('select-multiple', 'Select Multiple'),
                    ('select_image', 'Select Image'),
                    ('integer', 'integer'),
                    ('float', 'floating-point number'),
                    ('date', 'date'),
                    ('range_int', 'range (integers)'),
                    ('range_float', 'range (floating-point numbers)')
                ],
                default='text',
                max_length=200,
                verbose_name='Type'
            ),
        ),
        migrations.AlterField(
            model_name='question',
            name='order',
            field=models.IntegerField(
                blank=True,
                help_text='\n    Order of this question in the display (starting with 1).\n\
                        If none is specified, the question will be shown in a random order\n    ',
                null=True,
                verbose_name='Order'
            ),
        ),
        migrations.CreateModel(
            name='CategoryBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active?')),
                ('dt_created', models.DateTimeField(default=django.utils.timezone.now, help_text='Autofilled',
                                                    null=True, verbose_name='Created at')),
                ('dt_updated', models.DateTimeField(help_text='Autofilled', null=True, verbose_name='Updated at')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='booked_in_surveys',
                                               to='scientific_survey.category',
                                               verbose_name='Category')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='booked_categories',
                                             to='scientific_survey.survey',
                                             verbose_name='Survey')),
            ],
        ),
    ]
