# -*- coding: utf-8 -*-

import logging
import random
import uuid
from operator import itemgetter

from django import forms
from django.conf import settings
from django.db.models import Case, When
from django.forms import models
from django.urls import reverse
from django.utils.text import slugify

from scientific_survey.models import Answer, AnswerGroup, Category, CategoryBooking, Question, Response, Survey
from scientific_survey.signals import survey_completed
from scientific_survey.widgets import ImageSelectWidget, RangeWidget

LOGGER = logging.getLogger(__name__)


class ResponseForm(models.ModelForm):

    FIELDS = {
        AnswerGroup.TEXT: forms.CharField,
        AnswerGroup.SHORT_TEXT: forms.CharField,
        AnswerGroup.SELECT_MULTIPLE: forms.MultipleChoiceField,
        AnswerGroup.INTEGER: forms.IntegerField,
        AnswerGroup.FLOAT: forms.FloatField,
        AnswerGroup.DATE: forms.DateField,
        AnswerGroup.INTEGER_RANGE: forms.IntegerField,
        AnswerGroup.FLOAT_RANGE: forms.FloatField
    }

    WIDGETS = {
        AnswerGroup.TEXT: forms.Textarea,
        AnswerGroup.SHORT_TEXT: forms.TextInput,
        AnswerGroup.RADIO: forms.RadioSelect,
        AnswerGroup.SELECT: forms.Select,
        AnswerGroup.SELECT_IMAGE: ImageSelectWidget,
        AnswerGroup.SELECT_MULTIPLE: forms.CheckboxSelectMultiple,
        AnswerGroup.INTEGER_RANGE: RangeWidget,
        AnswerGroup.FLOAT_RANGE: RangeWidget
    }

    class Meta:
        model = Response
        fields = ()

    def __init__(self, *args, **kwargs):
        """ Expects a survey object to be passed in initially """
        self.survey = kwargs.pop("survey")
        self.user = kwargs.pop("user")
        self.extra = kwargs.pop("extra", "")
        self.scope_category_id = kwargs.pop("scope", "")
        try:
            self.step = int(kwargs.pop("step"))
        except KeyError:
            self.step = None

        try:
            self.random_seed = int(kwargs.pop("seed"))
        except (KeyError, ValueError, TypeError):
            self.random_seed = random.randint(0, 1000000)
        super(ResponseForm, self).__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex

        self.categories = self.survey.non_empty_categories()  # list

        self.qs_with_no_cat = self.survey.questions.filter(
            category__isnull=True).order_by("order", "id")

        self.questions_to_randomize = self.survey.questions.filter(order__isnull=True)
        self.ordered_questions = self.survey.questions.filter(order__isnull=False)

        self.__updated_scope_category = False
        self._try_scope_questions()

        self.questions_to_randomize = self.questions_to_randomize.order_by("id")
        self.ordered_questions = self.ordered_questions.order_by("order")
        self.__get_steps_count()

        # will contain prefetched data to avoid multiple db calls
        self.response = False
        self.answers = False

        self.answer_groups = {}
        self.questions_by_categories = {}

        self._get_preexisting_response()
        if self.response:
            self.random_seed = self.response.random_seed
            self.extra = self.response.extra
        elif self.__updated_scope_category:
            booking, is_created = CategoryBooking.objects.get_or_create(
                survey=self.survey, category_id=self.scope_category_id
            )
            if not is_created:
                booking.filled_slots += 1
                booking.save()

        self.add_questions(kwargs.get("data"))

        if not self.survey.editable_answers and self.response is not None:
            for name in self.fields.keys():
                self.fields[name].widget.attrs["disabled"] = True

    def __get_steps_count(self):
        if self.survey.display_method == Survey.BY_CATEGORY:
            self.steps_count = len(self.categories) + (1 if self.qs_with_no_cat else 0)
        else:
            self.steps_count = len(self.questions_to_randomize) + len(self.ordered_questions)

    def _try_scope_questions(self):
        if self.survey.categories_as_surveys:
            if not self.scope_category_id:
                self._try_find_scope_category()
            self.questions_to_randomize = self.questions_to_randomize.filter(category_id=self.scope_category_id)
            self.ordered_questions = self.ordered_questions.filter(category_id=self.scope_category_id)

    def _try_find_scope_category(self):
        cats2choose = self.survey.get_bookable_categories()
        if cats2choose:
            random.seed(self.random_seed)
            scope_category = random.choice(cats2choose)
            self.scope_category_id = scope_category.pk
            self.__updated_scope_category = True

    def get_ordered_question_ids(self, questions2order, questions2randomize):
        ordered_pairs = questions2order.values_list("id", "order").all()
        randomized_pairs = list(questions2randomize.values_list("id", "order").all())
        random.seed(self.random_seed)
        random.shuffle(randomized_pairs)

        for idx, order in ordered_pairs:
            randomized_pairs.insert(order - 1, (idx, order))

        return list(map(itemgetter(0), randomized_pairs))

    def add_questions(self, data):
        # add a field for each survey question, corresponding to the question
        # type as appropriate.

        if self.survey.display_method == Survey.BY_CATEGORY and self.step is not None:
            if self.step == len(self.categories):
                qs_for_step = self.qs_with_no_cat
            else:
                qs_for_step = self.survey.questions.filter(category=self.categories[self.step]).order_by("order", "id")

            ordered_ids = self.get_ordered_question_ids(
                qs_for_step.filter(order__isnull=False).order_by("order"),
                qs_for_step.filter(order__isnull=True).order_by("id"),
            )

            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)])
            for question in qs_for_step.order_by(preserved).all():
                self.add_question(question, data)
        else:
            self.ordered_questions.order_by("order").values_list("id", "order").all()
            list(self.questions_to_randomize.values_list("id", "order").all())

            ordered_ids = self.get_ordered_question_ids(self.ordered_questions, self.questions_to_randomize)

            if self.survey.display_method == Survey.BY_QUESTION and self.step is not None:
                question = self.survey.questions.filter(id=ordered_ids[self.step]).first()
                self.add_question(question, data)
            else:
                # If display method is all at once
                if self.categories:
                    qs_for_cat, ordered_ids = self.get_qs_for_cat()

                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)])
                if self.survey.categories_as_surveys:
                    for question in qs_for_cat.order_by(preserved).all():
                        self.add_question(question, data)
                else:
                    for question in self.survey.questions.order_by(preserved).all():
                        self.add_question(question, data)

    def get_qs_for_cat(self):
        if self.survey.categories_as_surveys:
            qs_for_cat = self.survey.questions.filter(
                category_id=self.scope_category_id).order_by("order", "id")
            ordered_ids = self.get_ordered_question_ids(
                qs_for_cat.filter(order__isnull=False).order_by("order"),
                qs_for_cat.filter(order__isnull=True).order_by("id"),
            )
            return qs_for_cat, ordered_ids
        else:
            # If additionally there are categories
            ordered_ids = []
            for cat in self.categories:
                qs_for_cat = self.survey.questions.filter(category=cat).order_by("order", "id")
                ordered_ids.extend(
                    self.get_ordered_question_ids(
                        qs_for_cat.filter(order__isnull=False).order_by("order"),
                        qs_for_cat.filter(order__isnull=True).order_by("id"),
                    )
                )
            return None, ordered_ids

    def current_categories(self):
        if self.survey.categories_as_surveys:
            return [Category.objects.get(pk=self.scope_category_id)]

        if self.survey.display_method == Survey.BY_CATEGORY:
            if self.step is not None and self.step < len(self.categories):
                return [self.categories[self.step]]
            return [Category(name="No category", description="No cat desc")]
        else:
            extras = []
            if self.qs_with_no_cat:
                extras = [Category(name="No category", description="No cat desc")]

            return self.categories + extras if self.categories else []

    def _get_preexisting_response(self):
        """Recover a pre-existing response in database.

        The user must be logged. Will store the response retrieved in an attribute
        to avoid multiple db calls.

        :rtype: Response or None"""
        if self.response:
            return self.response

        if not self.user.is_authenticated:
            self.response = None
        else:
            try:
                if self.survey.categories_as_surveys and self.survey.save_categories_separately:
                    self.response = Response.objects.prefetch_related("user", "survey").get(
                        user=self.user, survey=self.survey, category_id=self.scope_category_id
                    )
                else:
                    self.response = Response.objects.prefetch_related("user", "survey").get(
                        user=self.user, survey=self.survey, category__isnull=True
                    )
            except Response.DoesNotExist:
                LOGGER.debug("No saved response for '%s' for user %s", self.survey, self.user)
                self.response = None
        return self.response

    def _get_preexisting_answers(self):
        """Recover pre-existing answers in database.

        The user must be logged. A Response containing the Answer must exists.
        Will create an attribute containing the answers retrieved to avoid multiple
        db calls.

        :rtype: dict of Answer or None"""
        if self.answers:
            return self.answers

        response = self._get_preexisting_response()
        if response is None:
            self.answers = None
        try:
            answers = Answer.objects.filter(response=response).prefetch_related("question")
            self.answers = {}
            for answer in answers.all():
                if answer.question.id not in self.answers:
                    self.answers[answer.question.id] = {}
                self.answers[answer.question.id][answer.answer_group.id] = answer
        except Answer.DoesNotExist:
            self.answers = None

        return self.answers

    def _get_preexisting_answer(self, question, answer_group):
        """Recover a pre-existing answer in database.

        The user must be logged. A Response containing the Answer must exists.

        :param Question question: The question we want to recover in the
        response.
        :rtype: Answer or None"""
        answers = self._get_preexisting_answers()
        qanswers = answers.get(question.id, {})
        return qanswers.get(answer_group.id) if answer_group else qanswers

    def get_question_initial(self, question, data):
        """Get the initial value that we should use in the Form

        :param Question question: The question
        :param dict data: Value from a POST request.
        :rtype: String or None"""
        initial = {}
        answers = self._get_preexisting_answer(question, None)
        if answers:
            for ag_id, answer in answers.items():
                # Initialize the field with values from the database if any
                if answer.answer_group.type == AnswerGroup.SELECT_MULTIPLE:
                    initial[ag_id] = []
                    if answer.body == "[]":
                        pass
                    elif "[" in answer.body and "]" in answer.body:
                        initial[ag_id] = []
                        unformated_choices = answer.body[1:-1].strip()
                        for unformated_choice in unformated_choices.split(settings.CHOICES_SEPARATOR):
                            choice = unformated_choice.split("'")[1]
                            initial[ag_id].append(slugify(choice))
                    else:
                        # Only one element
                        initial[ag_id].append(slugify(answer.body))
                else:
                    initial[ag_id] = answer.body
        if data:
            # Initialize the field field from a POST request, if any.
            # Replace values from the database
            initial = data.get("question_%d" % question.pk)
        return initial

    def get_question_widget(self, question):
        """Return the widget we should use for a question.

        :param Question question: The question
        :rtype: django.forms.widget or None"""
        try:
            return {ag.pk: self.WIDGETS[ag.type] for ag in question.answer_groups.all()}
        except KeyError:
            return None

    @staticmethod
    def get_question_choices(question):
        """Return the choices we should use for a question.

        :param Question question: The question
        :rtype: List of String or None"""
        qchoices = {}
        for ag in question.answer_groups.all():
            if ag.type in [AnswerGroup.INTEGER_RANGE, AnswerGroup.FLOAT_RANGE]:
                qchoices[ag.pk] = ag.choices
            elif ag.type not in [
                AnswerGroup.TEXT,
                AnswerGroup.SHORT_TEXT,
                AnswerGroup.INTEGER,
                AnswerGroup.FLOAT,
                AnswerGroup.DATE,
            ]:
                choices = ag.get_choices()
                # add an empty option at the top so that the user has to explicitly
                # select one of the options
                if ag.type in [AnswerGroup.SELECT, AnswerGroup.SELECT_IMAGE]:
                    choices = tuple([("", "-------------")]) + choices
                if choices:
                    qchoices[ag.pk] = choices
        return qchoices or None

    def init_field(self, fkw, ag):
        field = None
        if ag.type == AnswerGroup.INTEGER_RANGE or ag.type == AnswerGroup.FLOAT_RANGE:
            choices = fkw.pop("choices")
            conv_func = int if ag.type == AnswerGroup.INTEGER_RANGE else float
            min_val, max_val, step = map(conv_func, choices.split(settings.CHOICES_SEPARATOR))
            fkw['min_value'] = min_val
            fkw['max_value'] = max_val

            field = self.FIELDS[ag.type](**fkw)
            setattr(field, "step_size", step)
        else:
            field = self.FIELDS[ag.type](**fkw)
        return field

    def get_question_fields(self, question, **kwargs):
        """Return the field we should use in our form.

        :param Question question: The question
        :param **kwargs: A dict of parameter properly initialized in
            add_question.
        :rtype: django.forms.fields"""
        # logging.debug("Args passed to field %s", kwargs)

        fields = []
        for ag in question.answer_groups.order_by("pk").all():
            fkw = dict(kwargs)
            if "initial" in fkw:
                if ag.pk in fkw["initial"]:
                    fkw["initial"] = fkw["initial"][ag.pk]
                else:
                    del fkw["initial"]
            if "choices" in fkw:
                if ag.pk in fkw["choices"]:
                    fkw["choices"] = fkw["choices"][ag.pk]
                else:
                    del fkw["choices"]
            if "widget" in fkw:
                if ag.pk in fkw["widget"]:
                    fkw["widget"] = fkw["widget"][ag.pk]
                else:
                    del fkw["widget"]
            fkw["label"] = ag.name
            try:
                field = self.init_field(fkw, ag)
                fields.append((ag, field))
            except KeyError:
                fields.append((ag, forms.ChoiceField(**fkw)))
        return fields

    def init_attrs(self, ag, field):
        if ag.type == AnswerGroup.DATE:
            field.widget.attrs["class"] = "date"
        elif ag.type == AnswerGroup.INTEGER_RANGE or ag.type == AnswerGroup.FLOAT_RANGE:
            field.widget.attrs['min_value'] = field.min_value
            field.widget.attrs['max_value'] = field.max_value
            field.widget.attrs['step_size'] = getattr(field, "step_size")

    def add_question(self, question, data):
        """Add a question to the form.

        :param Question question: The question to add.
        :param dict data: The pre-existing values from a post request."""
        kwargs = {"required": question.required}
        initial = self.get_question_initial(question, data)
        if initial:
            kwargs["initial"] = initial
        choices = self.get_question_choices(question)
        if choices:
            kwargs["choices"] = choices
        widget = self.get_question_widget(question)
        if widget:
            kwargs["widget"] = widget
        fields = self.get_question_fields(question, **kwargs)
        for ag, field in fields:
            field.widget.attrs["category"] = question.category.name if question.category else ""
            self.init_attrs(ag, field)
        # logging.debug("Field for %s : %s", question, field.__dict__)

        idq = "question_{}".format(question.pk)
        category_name = field.widget.attrs["category"]

        if category_name:
            if category_name not in self.questions_by_categories:
                self.questions_by_categories[category_name] = []
            self.questions_by_categories[category_name].append(idq)

        for ag, f in fields:
            idf = "question_{}_{}".format(question.pk, ag.pk)
            self.fields[idf] = f
            if idq not in self.answer_groups:
                self.answer_groups[idq] = {"text": question.text, "fields": []}
            self.answer_groups[idq]["fields"].append((idf, ag.prefix, ag.suffix))

    def has_next_step(self):
        if not self.survey.is_all_in_one_page():
            if self.step < self.steps_count - 1:
                return True
        return False

    def next_step_url(self):
        if self.has_next_step():
            context = {
                "id": self.survey.id,
                "step": self.step + 1,
                "seed": self.random_seed if self.questions_to_randomize else 0,
            }
            remainder = "?{}".format(self.extra) if self.extra else ""
            return reverse("survey-detail-step", kwargs=context) + remainder

    def current_step_url(self):
        remainder = "?{}".format(self.extra) if self.extra else ""
        return (
            reverse(
                "survey-detail-step",
                kwargs={
                    "id": self.survey.id,
                    "step": self.step,
                    "seed": self.random_seed if self.questions_to_randomize else 0,
                },
            )
            + remainder
        )

    def save(self, commit=True):
        """ Save the response object """
        # Recover an existing response from the database if any
        #  There is only one response by logged user.
        response = self._get_preexisting_response()
        if not self.survey.editable_answers and response is not None:
            return None
        if response is None:
            response = super(ResponseForm, self).save(commit=False)
        response.survey = self.survey
        response.interview_uuid = self.uuid
        response.random_seed = self.random_seed
        if self.survey.categories_as_surveys:
            response.category_id = self.scope_category_id
        if self.user.is_authenticated:
            response.user = self.user
        response.extra = self.extra
        response.save()
        # response "raw" data as dict (for signal)
        data = {"survey_id": response.survey.id, "interview_uuid": response.interview_uuid, "responses": []}
        # create an answer object for each question and associate it with this
        # response.
        for field_name, field_value in list(self.cleaned_data.items()):
            if field_name.startswith("question_"):
                # warning: this way of extracting the id is very fragile and
                # entirely dependent on the way the question_id is encoded in
                # the field name in the __init__ method of this form class.
                parts = field_name.split("_")
                q_id = int(parts[1])
                ag_id = int(parts[2])
                question = Question.objects.get(pk=q_id)
                answer_group = AnswerGroup.objects.get(pk=ag_id)
                answer = self._get_preexisting_answer(question, answer_group)
                if answer is None:
                    answer = Answer(question=question, answer_group=answer_group)
                if answer_group.type == AnswerGroup.SELECT_IMAGE:
                    value, img_src = field_value.split(":", 1)
                    # TODO Handling of SELECT IMAGE
                    LOGGER.debug("AnswerGroup.SELECT_IMAGE not implemented, please use : %s and %s", value, img_src)
                answer.body = field_value
                data["responses"].append((answer.question.id, answer.body))
                LOGGER.debug("Creating answer for question %d of type %s : %s", q_id, answer_group.type, field_value)
                answer.response = response
                answer.save()
        survey_completed.send(sender=Response, instance=response, data=data)
        return response

    @property
    def groups_by_question(self):
        return [(v["text"], [(self[k], p, s) for k, p, s in v["fields"]]) for v in self.answer_groups.values()]

    def groups_by_category(self, category_name):
        question_ids = self.questions_by_categories.get(category_name)
        if question_ids:
            return [
                (v["text"], [(self[k], p, s) for k, p, s in v["fields"]])
                for idq, v in self.answer_groups.items()
                if idq in question_ids
            ]
        else:
            return []

    @property
    def active_category_name(self):
        if self.survey.display_method == Survey.BY_QUESTION:
            # the questions_by_categories should have only one key
            assert (
                len(self.questions_by_categories.keys()) == 1
            ), "More than one question got categorized when displaying by question"
            return list(self.questions_by_categories.keys())[0]
        else:
            return None
