from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from splitio.impressions import build_impressions_data

_logger = logging.getLogger(__name__)


def report_impressions(impressions_cache, sdk_api):
    """If the reporting process is enabled (through the impressions cache), this function collects
    the impressions from the cache and sends them to Split through the events API. If the process
    fails, no exceptions are raised (but they are logged) and the process is disabled.
    """
    try:
        if not impressions_cache.is_enabled():
            return

        impressions = impressions_cache.fetch_all_and_clear()
        test_impressions_data = build_impressions_data(impressions)

        if len(test_impressions_data) > 0:
            _logger.info('Posting impressions for features: %s.', ', '.join(impressions.keys()))
            sdk_api.test_impressions(test_impressions_data)
    except:
        _logger.exception('Exception caught report impressions. Disabling impressions log.')
        impressions_cache.disable()
