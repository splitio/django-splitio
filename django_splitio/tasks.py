from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger

from splitio.segments import ApiSegmentChangeFetcher
from splitio.splits import ApiSplitChangeFetcher
from splitio.redis_support import (RedisSplitCache, RedisSegmentCache, RedisImpressionsCache,
                                   RedisMetricsCache, RedisSplitParser)
from splitio.tasks import (update_segments, update_splits, report_impressions, report_metrics)
from .settings import splitio_settings

logger = get_task_logger(__name__)


def get_features_update_schedule():
    """Returns the schedule for the features update task. This function should be called during
    the setup of CELERYBEAT_SCHEDULE.
    :return: The features update task schedule.
    """
    return timedelta(seconds=splitio_settings.CONFIG['featuresRefreshRate'])


def get_segments_update_schedule():
    """Returns the schedule for the segments update task. This function should be called during
    the setup of CELERYBEAT_SCHEDULE.
    :return: The segments update task schedule.
    """
    return timedelta(seconds=splitio_settings.CONFIG['segmentsRefreshRate'])


def get_impressions_update_schedule():
    """Returns the schedule for the impressions update task. This function should be called during
    the setup of CELERYBEAT_SCHEDULE.
    :return: The impressions update task schedule.
    """
    return timedelta(seconds=splitio_settings.CONFIG['impressionsRefreshRate'])


def get_metrics_update_schedule():
    """Returns the schedule for the metrics update task. This function should be called during
    the setup of CELERYBEAT_SCHEDULE.
    :return: The metrics update task schedule.
    """
    return timedelta(seconds=splitio_settings.CONFIG['metricsRefreshRate'])


@shared_task(name='django_splitio.tasks.update_features_task', ignore_result=True)
def update_features_task():
    try:
        redis = splitio_settings.redis_factory()
        split_cache = RedisSplitCache(redis)
        sdk_api = splitio_settings.api_factory()
        split_change_fetcher = ApiSplitChangeFetcher(sdk_api)
        segment_cache = RedisSegmentCache(redis)
        split_parser = RedisSplitParser(segment_cache)
        update_splits(split_cache, split_change_fetcher, split_parser)
    except:
        logger.exception('Exception caught running features update task')


@shared_task(name='django_splitio.tasks.update_segments_task', ignore_result=True)
def update_segments_task():
    try:
        redis = splitio_settings.redis_factory()
        segment_cache = RedisSegmentCache(redis)
        sdk_api = splitio_settings.api_factory()
        segment_change_fetcher = ApiSegmentChangeFetcher(sdk_api)
        update_segments(segment_cache, segment_change_fetcher)
    except:
        logger.exception('Exception caught running segment definitions update task')


@shared_task(name='django_splitio.tasks.update_impressions_task', ignore_result=True)
def update_impressions_task():
    try:
        redis = splitio_settings.redis_factory()
        impressions_cache = RedisImpressionsCache(redis)
        sdk_api = splitio_settings.api_factory()
        report_impressions(impressions_cache, sdk_api)
    except:
        logger.exception('Exception caught running impressions update task')


@shared_task(name='django_splitio.tasks.update_metrics_task', ignore_result=True)
def update_metrics_task():
    try:
        redis = splitio_settings.redis_factory()
        metrics_cache = RedisMetricsCache(redis)
        sdk_api = splitio_settings.api_factory()
        report_metrics(metrics_cache, sdk_api)
    except:
        logger.exception('Exception caught running metrics update task')
