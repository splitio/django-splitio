from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from splitio.metrics import AsyncMetrics, CacheBasedMetrics

from .cache import metrics_cache


_logger = logging.getLogger(__name__)


def report_metrics(a_metrics_cache, an_sdk_api):
    """If the reporting process is enabled (through the metrics cache), this function collects
    the time, count and gauge from the cache and sends them to Split through the events API. If the
    process fails, no exceptions are raised (but they are logged) and the process is disabled."""
    try:
        if not a_metrics_cache.is_enabled():
            return

        metrics = a_metrics_cache.fetch_all_and_clear()

        if 'time' in metrics and len(metrics['time']) > 0:
            _logger.info('Sending times metrics...')
            an_sdk_api.metrics_times(metrics['time'])

        if 'count' in metrics and len(metrics['count']) > 0:
            _logger.info('Sending counters metrics...')
            an_sdk_api.metrics_counters(metrics['count'])

        if 'gauge' in metrics and len(metrics['gauge']) > 0:
            _logger.info('Sending gauge metrics...')
            an_sdk_api.metrics_gauge(metrics['gauge'])
    except:
        _logger.exception('Exception caught reporting metrics')
        a_metrics_cache.disable()

metrics = AsyncMetrics(CacheBasedMetrics(metrics_cache))
