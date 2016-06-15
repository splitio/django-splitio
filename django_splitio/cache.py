from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings

from redis import StrictRedis


def default_redis_factory():
    """Default redis client factory. It uses the host, port and db configuration found on the
    REDIS_SETTINGS entry in the SPLITIO settings dictionary.
    :return: A StrictRedis object using the provided config values
    :rtype: StrictRedis
    """
    host = settings.SPLITIO.get('REDIS_HOST', 'localhost') or 'localhost'
    port = settings.SPLITIO.get('REDIS_PORT', 6379) or 6379
    db = settings.SPLITIO.get('REDIS_DB', 0) or 0
    redis = StrictRedis(host=host, port=port, db=db)
    return redis
