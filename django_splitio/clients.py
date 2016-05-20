from __future__ import absolute_import, division, print_function, unicode_literals

from splitio.clients import Client

from .features import split_fetcher
from .impressions import treatment_log
from .metrics import metrics


class DjangoCacheClient(Client):
    def __init__(self, a_split_fetcher, a_treatment_log, a_metrics):
        """A Client implementation that uses Django specific versions of split fetcher, treatment
        log and metrics."""
        super(DjangoCacheClient, self).__init__()
        self._split_fetcher = a_split_fetcher
        self._treatment_log = a_treatment_log
        self._metrics = a_metrics

    def get_split_fetcher(self):
        """
        Get the split fetcher implementation for the client.
        :return: The split fetcher
        :rtype: SplitFetcher
        """
        return self._split_fetcher

    def get_treatment_log(self):
        """
        Get the treatment log implementation for the client.
        :return: The treatment log
        :rtype: TreatmentLog
        """
        return self._treatment_log

    def get_metrics(self):
        """
        Get the metrics implementation for the client.
        :return: The metrics
        :rtype: Metrics
        """
        return self._metrics

client = DjangoCacheClient(split_fetcher, treatment_log, metrics)
