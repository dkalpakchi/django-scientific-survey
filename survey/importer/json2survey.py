import json

from django.conf import settings

from survey.models import AnswerGroup, Question, Survey


class Json2Survey:
    @staticmethod
    def import_from_file(jsonfile):
        data = json.load(jsonfile)
        s = Survey.objects.create(
            name=data["name"], is_published=True, need_logged_user=True, display_method=Survey.BY_QUESTION
        )
        for item in data["items"]:
            q = Question.objects.create(
                text=item["question"],
                extra=item.get("extra", {}),
                required=item["required"],
                order=item["order"] if item["order"] > 0 else None,
                survey=s,
            )
            for aset in item["answer_sets"]:
                AnswerGroup.objects.create(
                    type=aset["type"],
                    choices=settings.CHOICES_SEPARATOR.join(map(str, aset.get("choices", []))),
                    question=q,
                    name=aset["name"],
                    prefix=aset.get("prefix", ""),
                    suffix=aset.get("suffix", ""),
                )
