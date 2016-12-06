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
    password = settings.SPLITIO.get('REDIS_PASSWORD', None) or None

    socket_timeout = settings.SPLITIO.get('REDIS_SOCKET_TIMEOUT', None)
    socket_connect_timeout = settings.SPLITIO.get('REDIS_SOCKET_CONNECT_TIMEOUT', None)
    socket_keepalive = settings.SPLITIO.get('REDIS_SOCKET_KEEPALIVE', None)
    socket_keepalive_options = settings.SPLITIO.get('REDIS_SOCKET_KEEPALIVE_OPTIONS', None)
    connection_pool = settings.SPLITIO.get('REDIS_CONNECTION_POOL', None)
    unix_socket_path = settings.SPLITIO.get('REDIS_UNIX_SOCKET_PATH', None)
    encoding = settings.SPLITIO.get('REDIS_ENCODING', 'utf-8')
    encoding_errors = settings.SPLITIO.get('REDIS_ENCODING_ERRORS', 'strict')
    charset = settings.SPLITIO.get('REDIS_CHARSET', None)
    errors = settings.SPLITIO.get('REDIS_ERRORS', None)
    decode_responses = settings.SPLITIO.get('REDIS_DECODE_RESPONSES', False)
    retry_on_timeout = settings.SPLITIO.get('REDIS_RETRY_ON_TIMEOUT', False)
    ssl = settings.SPLITIO.get('REDIS_SSL', False)
    ssl_keyfile = settings.SPLITIO.get('REDIS_SSL_KEYFILE', None)
    ssl_certfile = settings.SPLITIO.get('REDIS_SSL_CERTFILE', None)
    ssl_cert_reqs = settings.SPLITIO.get('REDIS_SSL_CERT_REQS', None)
    ssl_ca_certs = settings.SPLITIO.get('REDIS_SSL_CA_CERTS', None)
    max_connections = settings.SPLITIO.get('REDIS_MAX_CONNECTIONS', None)

    redis = StrictRedis(host=host, port=port, db=db, password=password, socket_timeout=socket_timeout,
                 socket_connect_timeout=socket_connect_timeout,
                 socket_keepalive=socket_keepalive, socket_keepalive_options=socket_keepalive_options,
                 connection_pool=connection_pool, unix_socket_path=unix_socket_path,
                 encoding=encoding, encoding_errors=encoding_errors,
                 charset=charset, errors=errors,
                 decode_responses=decode_responses, retry_on_timeout=retry_on_timeout,
                 ssl=ssl, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile,
                 ssl_cert_reqs=ssl_cert_reqs, ssl_ca_certs=ssl_ca_certs,
                 max_connections=max_connections)
    return redis
