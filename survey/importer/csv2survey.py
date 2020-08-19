import csv

from survey.models import Question, Survey


class Csv2Survey:
    @staticmethod
    def import_from_file(csvfile):
        reader = csv.reader(csvfile, delimiter=",")
        name = next(reader)
        s = Survey.objects.create(
            name=name[0], is_published=True, need_logged_user=True, display_method=Survey.BY_QUESTION
        )
        for line in reader:
            qtype, question, order = line[0], line[1], line[2]
            try:
                order = int(order)
            except ValueError:
                order = -1
            choices = line[3:]
            Question.objects.create(
                text=question,
                required=False,
                order=order if order > 0 else None,
                survey=s,
                type=qtype,
                choices=",".join(choices),
            )
