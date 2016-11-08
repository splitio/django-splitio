from __future__ import absolute_import, division, print_function, unicode_literals

import importlib

from django.conf import settings

from splitio.config import DEFAULT_CONFIG, SDK_API_BASE_URL, EVENTS_API_BASE_URL


DEFAULTS = {
    'API_KEY': None,
    'SDK_API_BASE_URL': SDK_API_BASE_URL,
    'EVENTS_API_BASE_URL': EVENTS_API_BASE_URL,
    'SPLIT_SDK_MACHINE_NAME': None,
    'SPLIT_SDK_MACHINE_IP': None,
    'API_FACTORY': 'django_splitio.api.api_factory',
    'REDIS_FACTORY': 'django_splitio.cache.default_redis_factory',
    'CLIENT_FACTORY': 'django_splitio.clients.django_client_factory',
    'SPLIT_FACTORY': 'django_splitio.factories.django_split_factory',
    'DISABLED_PERIOD': 60 * 5,
    'CONFIG': DEFAULT_CONFIG
}


def import_from_string(val, setting_name):
    try:
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(
            "Could not import '%s' for SPLITIO setting '%s'. %s: %s." % (val, setting_name,
                                                                         e.__class__.__name__, e))


class SplitioSettings(object):
    def __init__(self, user_settings=None, defaults=None):
        if user_settings is not None:
            self._user_settings = user_settings
        self.defaults = defaults if defaults is not None else DEFAULTS

    @property
    def api_factory(self):
        if not hasattr(self, '_api_factory'):
            self._api_factory = import_from_string(self.API_FACTORY, 'API_FACTORY')
        return self._api_factory

    @property
    def redis_factory(self):
        if not hasattr(self, '_redis_factory'):
            self._redis_factory = import_from_string(self.REDIS_FACTORY, 'REDIS_FACTORY')
        return self._redis_factory

    @property
    def client_factory(self):
        if not hasattr(self, '_client_factory'):
            self._client_factory = import_from_string(self.CLIENT_FACTORY, 'CLIENT_FACTORY')
        return self._client_factory

    @property
    def split_factory(self):
        if not hasattr(self, '_split_factory'):
            self._split_factory = import_from_string(self.SPLIT_FACTORY, 'SPLIT_FACTORY')
        return self._split_factory

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'SPLITIO', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid SPLITIO setting: '%s'" % attr)

        try:
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        setattr(self, attr, val)
        return val
splitio_settings = SplitioSettings(user_settings=None, defaults=DEFAULTS)
