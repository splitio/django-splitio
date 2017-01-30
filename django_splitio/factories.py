from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings

from splitio.factories import get_factory as get_splitio_factory

def get_factory():
    """Returns a split.io client/manager factory implementation using the configuration given
        in the SPLITIO section of the Django settings.
        :return: A split.io client/manager factory implementation
        :rtype: splitio.factories.SplitFactory
        """
    # Get config from Django settings
    sdk_config = settings.SPLITIO

    api_key = ''
    if 'apiKey' in sdk_config:
      api_key = sdk_config['apiKey']

    return get_splitio_factory(api_key, config=sdk_config)
