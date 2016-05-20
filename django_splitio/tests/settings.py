from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock

import os

BASE_DIR = os.path.dirname(__file__)
SECRET_KEY = 'some_secret_key'
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'splitio',
    'splitio.tests',
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
SPLITIO = {
    'API_KEY': mock.MagicMock(),
    'SDK_API_BASE_URL': 'some_sdk_api_base_url',
    'EVENTS_API_BASE_URL': 'some_events_abi_base_url',
    'SPLIT_SDK_MACHINE_NAME': mock.MagicMock(),
    'SPLIT_SDK_MACHINE_IP': mock.MagicMock(),
    'REDIS_FACTORY': 'django_splitio.tests.utils.mock_redis_factory',
    'CONFIG': {
        'connectionTimeout': mock.MagicMock(),
        'readTimeout': mock.MagicMock(),
        'featuresRefreshRate': mock.MagicMock(),
        'segmentsRefreshRate': mock.MagicMock(),
        'metricsRefreshRate': mock.MagicMock(),
        'impressionsRefreshRate': mock.MagicMock(),
        'randomizeIntervals': False
    }
}
