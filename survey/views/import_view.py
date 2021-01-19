from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from survey.importer.json2survey import Json2Survey


@login_required
def import_from_json(request):
    f = request.FILES.get("survey_import")
    if f:
        # try:
        Json2Survey.import_from_file(f)
        messages.add_message(request, messages.SUCCESS, "The survey was successfully imported")
        # except Exception:
        #     messages.add_message(request, messages.ERROR, "Could not import a survey")
    return redirect(request.META.get("HTTP_REFERER"))
