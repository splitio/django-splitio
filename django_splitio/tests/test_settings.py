from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock

from django.test import TestCase
from django.conf import settings

from splitio.tests.utils import MockUtilsMixin

from django_splitio.settings import splitio_settings, SplitioSettings, DEFAULTS, DEFAULT_CONFIG
from django_splitio.tests.utils import redis


class SplitioSettingsDjangoSettingsTests(TestCase, MockUtilsMixin):
    def test_settings_api_key_is_used(self):
        """Test that splitio_settings.API_KEY is taken from Django settings"""
        self.assertEqual(settings.SPLITIO['API_KEY'], splitio_settings.API_KEY)

    def test_settings_sdk_api_base_url_is_used(self):
        """Test that splitio_settings.SDK_API_BASE_URL is taken from Django settings"""
        self.assertEqual(settings.SPLITIO['SDK_API_BASE_URL'], splitio_settings.SDK_API_BASE_URL)

    def test_settings_events_events_api_base_url_is_used(self):
        """Test that splitio_settings.EVENTS_API_BASE_URL is taken from Django settings"""
        self.assertEqual(settings.SPLITIO['EVENTS_API_BASE_URL'],
                         splitio_settings.EVENTS_API_BASE_URL)

    def test_settings_split_sdk_machine_name_is_used(self):
        """Test that splitio_settings.SPLIT_SDK_MACHINE_NAME is taken from Django settings"""
        self.assertEqual(settings.SPLITIO['SPLIT_SDK_MACHINE_NAME'],
                         splitio_settings.SPLIT_SDK_MACHINE_NAME)

    def test_settings_split_sdk_machine_ip_is_used(self):
        """Test that splitio_settings.SPLIT_SDK_MACHINE_IP is taken from Django settings"""
        self.assertEqual(settings.SPLITIO['SPLIT_SDK_MACHINE_IP'],
                         splitio_settings.SPLIT_SDK_MACHINE_IP)

    def test_redis_factory_is_used(self):
        """Test that splitio_settings.redis_factory is taken from Django settings"""
        self.assertEqual(redis, splitio_settings.redis_factory())

    def test_config_is_used(self):
        """Test that splitio_settings.CONFIG is taken from Django settings"""
        self.assertDictEqual(settings.SPLITIO['CONFIG'], splitio_settings.CONFIG)

    def test_fails_with_unknown_config_value(self):
        """Test that splitio_settings doesn't work with an unknown config value"""
        with self.assertRaises(AttributeError):
            splitio_settings.FOOBAR


fake_redis_factory = mock.MagicMock()


class SplitioSettingsUserSettingsTests(TestCase, MockUtilsMixin):
    def setUp(self):
        self.some_user_settings = mock.MagicMock()
        self.a_split_settings = SplitioSettings(user_settings=self.some_user_settings)

    def test_user_settings_api_key_used(self):
        """Test that split_settings uses the user supplied API_KEY value"""
        some_api_key = mock.MagicMock()
        self.some_user_settings.__getitem__.return_value = some_api_key
        self.assertEqual(some_api_key, self.a_split_settings.API_KEY)

    def test_user_settings_sdk_api_base_url_used(self):
        """Test that split_settings uses the user supplied SDK_API_BASE_URL value"""
        some_sdk_api_base_url = mock.MagicMock()
        self.some_user_settings.__getitem__.return_value = some_sdk_api_base_url
        self.assertEqual(some_sdk_api_base_url, self.a_split_settings.SDK_API_BASE_URL)

    def test_user_settings_events_api_base_url_used(self):
        """Test that split_settings uses the user supplied EVENTS_API_BASE_URL value"""
        some_events_api_base_url = mock.MagicMock()
        self.some_user_settings.__getitem__.return_value = some_events_api_base_url
        self.assertEqual(some_events_api_base_url, self.a_split_settings.EVENTS_API_BASE_URL)

    def test_user_settings_split_sdk_machine_name_used(self):
        """Test that split_settings uses the user supplied SPLIT_SDK_MACHINE_NAME value"""
        some_split_sdk_machine_name = mock.MagicMock()
        self.some_user_settings.__getitem__.return_value = some_split_sdk_machine_name
        self.assertEqual(some_split_sdk_machine_name, self.a_split_settings.SPLIT_SDK_MACHINE_NAME)

    def test_user_settings_split_sdk_machine_ip_used(self):
        """Test that split_settings uses the user supplied SPLIT_SDK_MACHINE_IP value"""
        some_split_sdk_machine_ip = mock.MagicMock()
        self.some_user_settings.__getitem__.return_value = some_split_sdk_machine_ip
        self.assertEqual(some_split_sdk_machine_ip, self.a_split_settings.SPLIT_SDK_MACHINE_IP)

    def test_redis_factory_is_used(self):
        """Test that splitio_settings.redis_factory is taken from the user settings"""
        self.some_user_settings.__getitem__.return_value = \
            'django_splitio.tests.test_settings.fake_redis_factory'
        self.assertEqual(fake_redis_factory.return_value, self.a_split_settings.redis_factory())

    def test_config_is_used(self):
        """Test that splitio_settings.CONFIG is taken from the user settings"""
        some_config = mock.MagicMock()
        self.some_user_settings.__getitem__.return_value = some_config
        self.assertEqual(some_config, self.a_split_settings.CONFIG)

    def test_fails_with_unknown_config_value(self):
        """Test that splitio_settings doesn't work with an unknown config value"""
        with self.assertRaises(AttributeError):
            self.a_split_settings.FOOBAR


class SplitioSettingsUserSettingsDefaultsTests(TestCase, MockUtilsMixin):
    def setUp(self):
        self.some_user_settings = mock.MagicMock()
        self.some_user_settings.__getitem__.side_effect = KeyError()
        self.a_split_settings = SplitioSettings(user_settings=self.some_user_settings)

    def test_user_settings_api_key_default_used(self):
        """Test that split_settings uses the default API_KEY value"""
        self.assertEqual(DEFAULTS['API_KEY'], self.a_split_settings.API_KEY)

    def test_user_settings_sdk_api_base_url_used(self):
        """Test that split_settings uses the default SDK_API_BASE_URL value"""
        self.assertEqual(DEFAULTS['SDK_API_BASE_URL'], self.a_split_settings.SDK_API_BASE_URL)

    def test_user_settings_events_api_base_url_used(self):
        """Test that split_settings uses the default EVENTS_API_BASE_URL value"""
        self.assertEqual(DEFAULTS['EVENTS_API_BASE_URL'], self.a_split_settings.EVENTS_API_BASE_URL)

    def test_user_settings_sdk_api_machine_name_used(self):
        """Test that split_settings uses the default SPLIT_SDK_MACHINE_NAME value"""
        self.assertEqual(DEFAULTS['SPLIT_SDK_MACHINE_NAME'],
                         self.a_split_settings.SPLIT_SDK_MACHINE_NAME)

    def test_user_settings_sdk_api_machine_ip_used(self):
        """Test that split_settings uses the default SPLIT_SDK_MACHINE_IP value"""
        self.assertEqual(DEFAULTS['SPLIT_SDK_MACHINE_IP'],
                         self.a_split_settings.SPLIT_SDK_MACHINE_IP)

    def test_redis_factory_is_used(self):
        """Test that splitio_settings.redis_factory is taken from default value"""
        default_redis_factory_mock = self.patch('django_splitio.cache.default_redis_factory')
        self.assertEqual(default_redis_factory_mock.return_value,
                         self.a_split_settings.redis_factory())

    def test_config_is_used(self):
        """Test that splitio_settings.CONFIG is taken from the defaults"""
        self.assertDictEqual(DEFAULT_CONFIG, self.a_split_settings.CONFIG)

    def test_fails_with_unknown_config_value(self):
        """Test that splitio_settings doesn't work with an unknown config value"""
        with self.assertRaises(AttributeError):
            self.a_split_settings.FOOBAR
