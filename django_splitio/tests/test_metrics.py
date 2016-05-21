from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock

from django.test import TestCase

from splitio.tests.utils import MockUtilsMixin

from django_splitio.metrics import report_metrics


class ReportMetricsTests(TestCase, MockUtilsMixin):
    def setUp(self):
        self.some_metrics_cache = mock.MagicMock()
        self.some_metrics_cache.is_enabled.return_value = True
        self.some_api_sdk = mock.MagicMock()

    def test_doenst_call_fetch_all_and_clear_if_disabled(self):
        """Test that report_metrics doesn't call fetch_all_and_clear if the cache is disabled"""
        self.some_metrics_cache.is_enabled.return_value = False
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_metrics_cache.fetch_all_and_clear.assert_not_called()

    def test_doesnt_call_metrics_times_if_disabled(self):
        """Test that report_metrics doesn't call metrics_times if the cache is disabled"""
        self.some_metrics_cache.is_enabled.return_value = False
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_api_sdk.metrics_times.assert_not_called()

    def test_doesnt_call_metrics_counters_if_disabled(self):
        """Test that report_metrics doesn't call metrics_counters if the cache is disabled"""
        self.some_metrics_cache.is_enabled.return_value = False
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_api_sdk.metrics_counters.assert_not_called()

    def test_doesnt_call_metrics_gauge_if_disabled(self):
        """Test that report_metrics doesn't call metrics_gauge if the cache is disabled"""
        self.some_metrics_cache.is_enabled.return_value = False
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_api_sdk.metrics_gauge.assert_not_called()

    def test_doesnt_call_metrics_times_if_time_metrics_is_empty(self):
        """Test that report_metrics doesn't call metrics_times if time metrics are empty"""
        self.some_metrics_cache.fetch_all_and_clear.return_value = {'time': [],
                                                                    'count': mock.MagicMock(),
                                                                    'gauge': mock.MagicMock()}
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_api_sdk.metrics_times.assert_not_called()

    def test_calls_metrics_times(self):
        """Test that report_metrics calls metrics_times if time metrics are not empty"""
        self.some_metrics_cache.fetch_all_and_clear.return_value = {'time': [mock.MagicMock()],
                                                                    'count': mock.MagicMock(),
                                                                    'gauge': mock.MagicMock()}
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_api_sdk.metrics_times.assert_called_once_with(
            self.some_metrics_cache.fetch_all_and_clear.return_value['time'])

    def test_doesnt_call_metrics_counters_if_counter_metrics_is_empty(self):
        """Test that report_metrics doesn't call metrics_counters if counter metrics are empty"""
        self.some_metrics_cache.fetch_all_and_clear.return_value = {'time': mock.MagicMock(),
                                                                    'count': [],
                                                                    'gauge': mock.MagicMock()}
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_api_sdk.metrics_counters.assert_not_called()

    def test_calls_metrics_counters(self):
        """Test that report_metrics calls metrics_counters if counter metrics are not empty"""
        self.some_metrics_cache.fetch_all_and_clear.return_value = {'time': mock.MagicMock(),
                                                                    'count': [mock.MagicMock()],
                                                                    'gauge': mock.MagicMock()}
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_api_sdk.metrics_counters.assert_called_once_with(
            self.some_metrics_cache.fetch_all_and_clear.return_value['count'])

    def test_doesnt_call_metrics_gauge_if_gauge_metrics_is_empty(self):
        """Test that report_metrics doesn't call metrics_gauge if counter metrics are empty"""
        self.some_metrics_cache.fetch_all_and_clear.return_value = {'time': mock.MagicMock(),
                                                                    'count': mock.MagicMock(),
                                                                    'gauge': []}
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_api_sdk.metrics_gauge.assert_not_called()

    def test_calls_metrics_gauge(self):
        """Test that report_metrics calls metrics_gauge if gauge metrics are not empty"""
        self.some_metrics_cache.fetch_all_and_clear.return_value = {'time': mock.MagicMock(),
                                                                    'count': mock.MagicMock(),
                                                                    'gauge': [mock.MagicMock()]}
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_api_sdk.metrics_gauge.assert_called_once_with(
            self.some_metrics_cache.fetch_all_and_clear.return_value['gauge'])

    def test_disables_cache_if_exception_is_raised(self):
        """Test that report_metrics disables cache if exception is raised"""
        self.some_metrics_cache.fetch_all_and_clear.side_effect = Exception()
        report_metrics(self.some_metrics_cache, self.some_api_sdk)
        self.some_metrics_cache.disable.assert_called_once_with()
