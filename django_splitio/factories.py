from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings

from splitio.factories import get_factory as get_splitio_factory

from .settings import splitio_settings


def django_split_factory():
    """Returns a split.io client/manager factory implementation using the configuration given
        in the SPLITIO section of the Django settings.
        :return: A split.io client/manager factory implementation
        :rtype: splitio.factories.SplitFactory
        """

    if splitio_settings.API_KEY == 'localhost':
        return get_splitio_factory('localhost')

    host = settings.SPLITIO.get('REDIS_HOST', 'localhost') or 'localhost'
    port = settings.SPLITIO.get('REDIS_PORT', 6379) or 6379
    db = settings.SPLITIO.get('REDIS_DB', 0) or 0

    sdk_config = {'redisHost': host, 'redisPort': port, 'redisDb': db}

    return get_splitio_factory(splitio_settings.API_KEY, config=sdk_config)

def get_factory():
    """Returns a split.io factory implementation based on the configuration given on the Django
    settings.
    :return: A split.io Factory implementation
    :rtype: SplitFactory
    """
    return splitio_settings.split_factory()