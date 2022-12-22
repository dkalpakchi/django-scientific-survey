from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from scientific_survey.importer.yaml2survey import Yaml2Survey


@login_required
def import_from_yaml(request):
    f = request.FILES.get("survey_import")
    if f:
        try:
            errors = Yaml2Survey.import_from_file(f, request.user)
            if not errors:
                messages.add_message(request, messages.SUCCESS, "The survey was successfully imported")
        except Exception:
            messages.add_message(
                request, messages.ERROR, "Could not import a survey, please check that the format is correct"
            )
        for e in errors:
            messages.add_message(request, messages.ERROR, e)
    return redirect(request.META.get("HTTP_REFERER"))
