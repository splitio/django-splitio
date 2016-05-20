from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from splitio.metrics import AsyncMetrics, CacheBasedMetrics

from .api import sdk_api
from .cache import metrics_cache


_logger = logging.getLogger(__name__)


def report_metrics():
    """If the reporting process is enabled (through the metrics cache), this function collects
    the time, count and gauge from the cache and sends them to Split through the events API. If the
    process fails, no exceptions are raised (but they are logged) and the process is disabled."""
    try:
        if not metrics_cache.is_enabled():
            return

        metrics = metrics_cache.fetch_all_and_clear()

        if 'time' in metrics and len(metrics['time']) > 0:
            _logger.info('Sending times metrics...')
            sdk_api.metrics_times(metrics['time'])

        if 'count' in metrics and len(metrics['count']) > 0:
            _logger.info('Sending counters metrics...')
            sdk_api.metrics_counters(metrics['count'])

        if 'gauge' in metrics and len(metrics['gauge']) > 0:
            _logger.info('Sending gauge metrics...')
            sdk_api.metrics_gauge(metrics['gauge'])
    except:
        _logger.exception('Exception caught reporting metrics')
        metrics_cache.disable()

metrics = AsyncMetrics(CacheBasedMetrics(metrics_cache))