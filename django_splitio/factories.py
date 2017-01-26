from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings

from splitio.factories import get_factory as get_splitio_factory

from .settings import splitio_settings


def django_split_factory():
    """Returns a split.io client/manager factory implementation using the configuration given
        in the SPLITIO section of the Django settings.
        :return: A split.io client/manager factory implementation
        :rtype: splitio.factories.SplitFactory
        """

    if splitio_settings.API_KEY == 'localhost':
        return get_splitio_factory('localhost')

    #sdk_config = settings.SPLITIO
    sdk_config = {
        'labelsEnabled': settings.SPLITIO.get('LABELS_ENABLED', True),
        'redisHost': settings.SPLITIO.get('REDIS_HOST', 'localhost'),
        'redisPort': settings.SPLITIO.get('REDIS_PORT', 6379),
        'redisDb': settings.SPLITIO.get('REDIS_DB', 0),
        'redisPassword': settings.SPLITIO.get('REDIS_PASSWORD', None),
        'redisSocketTimeout': settings.SPLITIO.get('REDIS_SOCKET_TIMEOUT', None),
        'redisSocketConnectTimeout': settings.SPLITIO.get('REDIS_SOCKET_CONNECT_TIMEOUT', None),
        'redisSocketKeepalive': settings.SPLITIO.get('REDIS_SOCKET_KEEPALIVE', None),
        'redisSocketKeepaliveOptions': settings.SPLITIO.get('REDIS_SOCKET_KEEPALIVE_OPTIONS', None),
        'redisConnectionPool': settings.SPLITIO.get('REDIS_CONNECTION_POOL', None),
        'redisUnixSocketPath': settings.SPLITIO.get('REDIS_UNIX_SOCKET_PATH', None),
        'redisEncoding': settings.SPLITIO.get('REDIS_ENCODING', 'utf-8'),
        'redisEncodingErrors': settings.SPLITIO.get('REDIS_ENCODING_ERRORS', 'strict'),
        'redisCharset': settings.SPLITIO.get('REDIS_CHARSET', None),
        'redisErrors': settings.SPLITIO.get('REDIS_ERRORS', None),
        'redisDecodeResponses': settings.SPLITIO.get('REDIS_DECODE_RESPONSES', False),
        'redisRetryOnTimeout': settings.SPLITIO.get('REDIS_RETRY_ON_TIMEOUT', False),
        'redisSsl': settings.SPLITIO.get('REDIS_SSL', False),
        'redisSslKeyfile': settings.SPLITIO.get('REDIS_SSL_KEYFILE', None),
        'redisSslCertfile': settings.SPLITIO.get('REDIS_SSL_CERTFILE', None),
        'redisSslCertReqs': settings.SPLITIO.get('REDIS_SSL_CERT_REQS', None),
        'redisSslCaCerts': settings.SPLITIO.get('REDIS_SSL_CA_CERTS', None),
        'redisMaxConnections': settings.SPLITIO.get('REDIS_MAX_CONNECTIONS', None)
    }

    #If Redis factory has been set, add it to sdk_config.
    if settings.SPLITIO.get('REDIS_FACTORY', False):
        sdk_config['redisFactory'] = settings.SPLITIO.get('REDIS_FACTORY')

    return get_splitio_factory(splitio_settings.API_KEY, config=sdk_config)

def get_factory():
    """Returns a split.io factory implementation based on the configuration given on the Django
    settings.
    :return: A split.io Factory implementation
    :rtype: SplitFactory
    """
    return splitio_settings.split_factory()