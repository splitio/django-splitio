from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock


redis = mock.MagicMock(name='mock_redis')


def mock_redis_factory():
    """A redis factory that returns a MagicMock"""
    return redis
