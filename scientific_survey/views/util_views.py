from django.shortcuts import render


def survey_full(request):
    return render(request, "scientific_survey/survey_full.html")


def survey_error(request):
    return render(request, "scientific_survey/survey_error.html")
