import json

from django.conf import settings

from scientific_survey.models import AnswerGroup, Category, Question, Survey


class Json2Survey:
    @staticmethod
    def import_from_file(jsonfile):
        data = json.load(jsonfile)
        s = Survey.objects.create(
            name=data["name"], is_published=True, need_logged_user=True, display_method=Survey.BY_QUESTION
        )

        categories = []
        for cname in data.get("categories", []):
            c = Category.objects.create(name=cname, survey=s)
            categories.append(c)

        for item in data["items"]:
            q = Question.objects.create(
                text=item["question"],
                extra=item.get("extra", {}),
                required=item["required"],
                order=item["order"] if item["order"] > 0 else None,
                survey=s,
            )

            try:
                cid = int(item.get("category"))
                q.category = categories[cid - 1]
                q.save()
            except IndexError:
                pass
            except TypeError:
                pass
            except ValueError:
                pass

            for aset in item["answer_sets"]:
                AnswerGroup.objects.create(
                    type=aset["type"],
                    choices=settings.CHOICES_SEPARATOR.join(map(str, aset.get("choices", []))),
                    question=q,
                    name=aset["name"],
                    prefix=aset.get("prefix", ""),
                    suffix=aset.get("suffix", ""),
                )
