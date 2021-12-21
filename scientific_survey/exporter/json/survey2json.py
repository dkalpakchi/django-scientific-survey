import codecs
import json
from collections import defaultdict

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from scientific_survey.exporter.survey2x import Survey2X


class Survey2Json(Survey2X):
    def __str__(self):
        res = {"name": self.survey.name, "responses": []}
        for response in self.survey.responses.all():
            user_answers = {}
            try:
                user_answers["user"] = response.user.username
            except AttributeError:
                # 'NoneType' object has no attribute 'username'
                user_answers["user"] = str(_("Anonymous"))
            user_answers["extra"] = response.extra
            user_answers["random_seed"] = response.random_seed

            user_answers["responses"] = defaultdict(list)
            for answer in response.answers.all():
                extra, body = answer.question.extra, answer.body
                try:
                    extra = json.loads(extra.replace("'", '"'))
                except (json.JSONDecodeError, AttributeError):
                    pass

                try:
                    body = json.loads(body.replace("'", '"'))
                except (json.JSONDecodeError, AttributeError):
                    pass

                user_answers["responses"][answer.question.text].append(
                    {"answer_group": answer.answer_group.name, "value": body, "extra": extra}
                )
            res["responses"].append(user_answers)
        return json.dumps(res)

    @staticmethod
    def export_as_json(modeladmin, request, queryset):
        response = HttpResponse(content_type="application/json")
        response.write(codecs.BOM_UTF8)
        filename = ""
        for i, survey in enumerate(queryset):
            survey_as_json = Survey2Json(survey)
            if i == 0:
                filename = survey.safe_name
            if len(queryset) == 1:
                response.write(survey_as_json)
            else:
                response.write("{survey_name}\n".format(survey_name=survey.name))
                response.write(survey_as_json)
                response.write("\n\n")
        response["Content-Disposition"] = "attachment; filename={}.json".format(filename)
        return response


Survey2Json.export_as_json.short_description = _("Export to JSON")
