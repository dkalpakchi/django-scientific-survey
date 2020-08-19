from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from survey.importer.csv2survey import Csv2Survey


@login_required
def import_from_csv(request):
    f = request.FILES.get("survey_import")
    if f:
        try:
            f_decoded = f.read().decode("utf8").splitlines()
            Csv2Survey.import_from_file(f_decoded)
            messages.add_message(request, messages.SUCCESS, "The survey was successfully imported")
        except Exception:
            messages.add_message(request, messages.ERROR, "Could not import a survey")
    return redirect(request.META.get("HTTP_REFERER"))
