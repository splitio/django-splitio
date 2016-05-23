from __future__ import absolute_import, division, print_function, unicode_literals


def get_client():
    """Returns a split.io client implementation based on the configuration given on the Django
    settings.
    :return: A split.io client implementation
    :rtype: Client
    """
    from .settings import splitio_settings
    return splitio_settings.client_factory()
