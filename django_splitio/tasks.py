from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger

from .features import update_segments, update_splits
from .impressions import report_impressions
from .metrics import report_metrics
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
        update_splits()
    except:
        logger.exception('Exception caught running features update task')


@shared_task(name='django_splitio.tasks.update_segments_task', ignore_result=True)
def update_segments_task():
    try:
        update_segments()
    except:
        logger.exception('Exception caught running segment definitions update task')


@shared_task(name='django_splitio.tasks.update_impressions_task', ignore_result=True)
def update_impressions_task():
    try:
        report_impressions()
    except:
        logger.exception('Exception caught running impressions update task')


@shared_task(name='django_splitio.tasks.update_metrics_task', ignore_result=True)
def update_metrics_task():
    try:
        report_metrics()
    except:
        logger.exception('Exception caught running metrics update task')
