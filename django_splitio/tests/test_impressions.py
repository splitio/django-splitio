from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock

from django.test import TestCase

from splitio.tests.utils import MockUtilsMixin

from django_splitio.impressions import report_impressions


class ReportImpressionsTests(TestCase, MockUtilsMixin):
    def setUp(self):
        self.build_impressions_data_mock = self.patch(
            'django_splitio.impressions.build_impressions_data')
        self.some_impressions_cache = mock.MagicMock()
        self.some_impressions_cache.is_enabled.return_value = True
        self.some_api_sdk = mock.MagicMock()

    def test_calls_is_enabled(self):
        """Test that report_impressions call is_enabled"""
        report_impressions(self.some_impressions_cache, self.some_api_sdk)
        self.some_impressions_cache.is_enabled.assert_called_once_with()

    def test_doesnt_call_fetch_all_and_clear_if_disabled(self):
        """Test that report_impressions doesn't call fetch_all_and_clear if the cache is disabled"""
        self.some_impressions_cache.is_enabled.return_value = False
        report_impressions(self.some_impressions_cache, self.some_api_sdk)
        self.some_impressions_cache.fetch_all_and_clear.assert_not_called()

    def test_doesnt_call_test_impressions_if_disabled(self):
        """Test that report_impressions doesn't call test_impressions if the cache is disabled"""
        self.some_impressions_cache.is_enabled.return_value = False
        report_impressions(self.some_impressions_cache, self.some_api_sdk)
        self.some_api_sdk.test_impressions.assert_not_called()

    def test_calls_fetch_all_and_clear(self):
        """Test that report_impressions calls fetch_all_and_clear"""
        report_impressions(self.some_impressions_cache, self.some_api_sdk)
        self.some_impressions_cache.fetch_all_and_clear.assert_called_once_with()

    def test_calls_build_impressions_data(self):
        """Test that report_impressions calls build_impressions_data_mock"""
        report_impressions(self.some_impressions_cache, self.some_api_sdk)
        self.build_impressions_data_mock.assert_called_once_with(
            self.some_impressions_cache.fetch_all_and_clear.return_value)

    def test_doesnt_call_test_impressions_if_data_is_empty(self):
        """Test that report_impressions doesn't call test_impressions if build_impressions_data
        returns an empty list"""
        self.build_impressions_data_mock.return_value = []
        report_impressions(self.some_impressions_cache, self.some_api_sdk)
        self.some_api_sdk.test_impressions.assert_not_called()

    def test_calls_test_impressions(self):
        """Test that report_impressions calls test_impression with the result of
        build_impressions_data"""
        self.build_impressions_data_mock.return_value = [mock.MagicMock()]
        report_impressions(self.some_impressions_cache, self.some_api_sdk)
        self.some_api_sdk.test_impressions.assert_called_once_with(
            self.build_impressions_data_mock.return_value)

    def test_cache_disabled_if_exception_is_raised(self):
        """Test that report_impressions disables the cache if an exception is raised"""
        self.build_impressions_data_mock.side_effect = Exception()
        report_impressions(self.some_impressions_cache, self.some_api_sdk)
        self.some_impressions_cache.disable.assert_called_once_with()
