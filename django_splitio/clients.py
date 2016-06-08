from __future__ import absolute_import, division, print_function, unicode_literals

from splitio.clients import Client, LocalhostEnvironmentClient

from splitio.impressions import AsyncTreatmentLog, CacheBasedTreatmentLog
from splitio.metrics import AsyncMetrics, CacheBasedMetrics
from splitio.splits import CacheBasedSplitFetcher

from .cache import RedisSplitCache, RedisImpressionsCache, RedisMetricsCache
from .settings import splitio_settings


class DjangoClient(Client):
    def __init__(self, a_split_fetcher, a_treatment_log, a_metrics):
        """A Client implementation that uses Django specific versions of split fetcher, treatment
        log and metrics."""
        super(DjangoClient, self).__init__()
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


def django_client_factory():
    """Returns a Django/Redis based split.io client implementation using the configuration given
    in the SPLITIO section of the Django settings.
    :return: A Django/Redis split.io client
    :rtype: DjangoClient
    """
    redis = splitio_settings.redis_factory()

    split_cache = RedisSplitCache(redis)
    split_fetcher = CacheBasedSplitFetcher(split_cache)

    impressions_cache = RedisImpressionsCache(splitio_settings.redis_factory())
    delegate_treatment_log = CacheBasedTreatmentLog(impressions_cache)
    treatment_log = AsyncTreatmentLog(delegate_treatment_log)

    metrics_cache = RedisMetricsCache(redis)
    delegate_metrics = CacheBasedMetrics(metrics_cache)
    metrics = AsyncMetrics(delegate_metrics)

    return DjangoClient(split_fetcher, treatment_log, metrics)


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
