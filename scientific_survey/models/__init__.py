# -*- coding: utf-8 -*-

"""
Permit to import everything from survey.models without knowing the details.
"""

from .answer import Answer
from .answer_group import AnswerGroup
from .category import Category, CategoryBooking
from .question import Layout, Question
from .response import Response
from .survey import Survey

__all__ = [
    "Category", "Answer", "Category", "CategoryBooking", "Response", "Survey", "Question", "AnswerGroup", "Layout"
]
