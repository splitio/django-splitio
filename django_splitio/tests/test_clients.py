from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock

from django.test import TestCase

from django_splitio.clients import client
from django_splitio.features import split_fetcher
from django_splitio.impressions import treatment_log
from django_splitio.metrics import metrics


class SingletonsTests(TestCase):
    def test_client_get_split_fetcher_returns_singleton_split_fetcher(self):
        """Tests that the client singleton get_split_fetcher returns the split_fetcher singleton"""
        self.assertEqual(client.get_split_fetcher(), split_fetcher)

    def test_client_get_treatment_log_returns_singleton_treatment_log(self):
        """Tests that the client singleton get_treatment_log returns the treatment_log singleton"""
        self.assertEqual(client.get_treatment_log(), treatment_log)

    def test_client_get_metrics_returns_singleton_metrics(self):
        """Tests that the client singleton get_treatment_log returns the treatment_log singleton"""
        self.assertEqual(client.get_metrics(), metrics)
