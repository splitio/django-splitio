from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from splitio.impressions import build_impressions_data, AsyncTreatmentLog, CacheBasedTreatmentLog

from .api import sdk_api
from .cache import impressions_cache

_logger = logging.getLogger(__name__)


def report_impressions(an_impressions_cache):
    """If the reporting process is enabled (through the impressions cache), this function collects
    the impressions from the cache and sends them to Split through the events API. If the process
    fails, no exceptions are raised (but they are logged) and the process is disabled.
    """
    try:
        if not an_impressions_cache.is_enabled():
            return

        impressions = an_impressions_cache.fetch_all_and_clear()
        test_impressions_data = build_impressions_data(impressions)

        if len(test_impressions_data) > 0:
            _logger.info('Posting impressions for features: %s.', ', '.join(impressions.keys()))
            sdk_api.test_impressions(test_impressions_data)
    except:
        _logger.exception('Exception caught report impressions. Disabling impressions log.')
        an_impressions_cache.disable()


treatment_log = AsyncTreatmentLog(CacheBasedTreatmentLog(impressions_cache))
