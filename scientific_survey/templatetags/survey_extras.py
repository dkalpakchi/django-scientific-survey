# -*- coding: utf-8 -*-

from django import template

register = template.Library()


def collapse_form(form, category):
    """Permit to return the class of the collapsible according to errors in
    the form."""
    categories_with_error = set()
    for field in form:
        if field.errors:
            categories_with_error.add(field.field.widget.attrs["category"])
    if category.name in categories_with_error:
        return "in"
    return ""


register.filter("collapse_form", collapse_form)


def get_by_key(dictionary, key):
    return dictionary[key]


register.filter("get_by_key", get_by_key)


def items(dictionary):
    return dictionary.items()


register.filter("items", items)


class CounterNode(template.Node):
    def __init__(self):
        self.count = 0

    def render(self, context):
        self.count += 1
        return self.count


@register.tag
def counter(parser, token):
    return CounterNode()


@register.filter(name="groups_by_category")
def groups_by_category(form, name):
    return form.groups_by_category(name)
