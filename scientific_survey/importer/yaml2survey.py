import yaml
from django.conf import settings
from django.db.models import Q

from scientific_survey.models import AnswerGroup, Category, Layout, Question, Survey


def extract_templates(layouts, user):
    templates = {}
    for codename, layout in layouts.items():
        if isinstance(layout, str):
            templates[codename] = layout
            Layout.objects.get_or_create(
                   codename=codename, template=layout,
                   owner=user, is_public=False
            )
        elif isinstance(layout, dict):
            templates[codename] = layout['template']
            if layout.get('save', False):
                Layout.objects.get_or_create(
                        codename=codename, template=templates[codename],
                        owner=user, is_public=layout.get('public', False)
                )
    return templates


def extract_question_text(item, templates, user):
    question_text, errors = None, set()
    if isinstance(item["question"], str):
        question_text = item["question"]
    elif isinstance(item["question"], dict):
        layout_code = item["question"].get("layout")
        template = templates.get(layout_code)
        if template is None:
            # Attempt to get from the DB
            layout = Layout.objects.filter(
                codename=layout_code
            ).filter(Q(owner=user) | Q(is_public=True))

            if layout.count() > 0:
                template = layout.first().template

        if template:
            try:
                question_text = template.format(**item["question"].get('scope', {}))
            except KeyError:
                errors.add("A question {} has incomplete scope".format(item['question']))

        if question_text is None:
            if layout_code:
                errors.add("Couldn't find a layout {}".format(layout_code))
            else:
                errors.add("No layout specified for {}".format(item['question']))
    return question_text, errors


class Yaml2Survey:
    @staticmethod
    def import_from_file(yaml_file, user):
        error_messages = set()
        data = yaml.safe_load(yaml_file)

        templates = extract_templates(data.get('layouts', {}), user)

        survey = Survey.objects.create(
            name=data["name"], is_published=True,
            need_logged_user=True, display_method=Survey.BY_QUESTION
        )

        categories = []
        for cname in data.get("categories", []):
            categories.append(Category.objects.create(name=cname, survey=survey))

        for item in data["items"]:
            question_text, errors = extract_question_text(item, templates, user)
            error_messages = error_messages | errors
            if errors:
                continue

            question = Question.objects.create(
                text=question_text,
                extra=item.get("extra", {}),
                required=item["required"],
                order=item["order"] if item["order"] > 0 else None,
                survey=survey,
            )

            try:
                cid = int(item.get("category"))
                question.category = categories[cid - 1]
                question.save()
            except IndexError:
                pass
            except TypeError:
                pass
            except ValueError:
                pass

            for aset in item["answer_sets"]:
                choices = aset.get("choices", [])
                AnswerGroup.objects.create(
                    type=aset["type"],
                    choices=settings.CHOICES_SEPARATOR.join(map(str, choices)),
                    question=question,
                    name=aset["name"],
                    prefix=aset.get("prefix", ""),
                    suffix=aset.get("suffix", ""),
                )
        if error_messages:
            survey.delete()
        return list(error_messages)
