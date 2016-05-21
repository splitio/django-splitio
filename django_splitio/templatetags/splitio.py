from __future__ import absolute_import, division, print_function, unicode_literals

from django import template
from django_splitio.clients import client

register = template.Library()


@register.simple_tag()
def get_treatment(key, feature, **kwargs):
    """A simple tag to get the treatment for a given key, feature and attributes. The following
    snippet

    {% load splitio %}
    {% get_treatment "some_key" "some_feature" some_attribute=42 %}

    renders the output of calling

    client.get_treatment('some_key', 'some_feature, {'some_attribute': 42})

    onto the template.
    :param key: The key
    :type key: str
    :param feature: The feature
    :type feature: str
    :param kwargs: Additional keyword arguments are going to be passed as attributes
    :return: The treatment for the key, feature and attributes
    """
    return client.get_treatment(key, feature, kwargs)


@register.assignment_tag
def set_treatment_for(key, feature, **kwargs):
    """An assignment tag to set the treatment for a given key, feature and attributes as a context
    variable. The following snippet

    {% load splitio %}
    {% set_treatment_for "some_key" "some_feature" some_attribute=42 as the_treatment %}

    sets the value of set_treatment in the page context to the result of calling

    client.get_treatment('some_key', 'some_feature, {'some_attribute': 42}).
    :param key: The key
    :type key: str
    :param feature: The feature
    :type feature: str
    :param kwargs: Additional keyword arguments are going to be passed as attributes
    :return: The treatment for the key, feature and attributes
    """
    return client.get_treatment(key, feature, kwargs)
