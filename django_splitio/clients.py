from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings as django_settings

from splitio.clients import RedisClient, Client, LocalhostEnvironmentClient

from .settings import splitio_settings


def django_client_factory():
    """Returns a Django/Redis based split.io client implementation using the configuration given
    in the SPLITIO section of the Django settings.
    :return: A Django/Redis split.io client
    :rtype: DjangoClient
    """
    if splitio_settings.API_KEY == 'localhost':
        return localhost_client_factory()

    redis = splitio_settings.redis_factory()

    labels_enabled = django_settings.SPLITIO.get('LABELS_ENABLED', True) or True

    return RedisClient(redis, labels_enabled)


def localhost_client_factory():
    """Returns a split.io client implementation that builds its configuration from a split
    definition file
    :return: A localhost environment split.io client.
    :rtype: LocalhostEnvironmentClient
    """
    return LocalhostEnvironmentClient()


def get_client():
    """Returns a split.io client implementation based on the configuration given on the Django
    settings.
    :return: A split.io client implementation
    :rtype: Client
    """
    return splitio_settings.client_factory()
