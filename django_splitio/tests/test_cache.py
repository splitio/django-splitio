from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock

from django.test import TestCase
from django.conf import settings

from splitio.tests.utils import MockUtilsMixin

from django_splitio.cache import (segment_cache, split_cache, impressions_cache, metrics_cache,
                                  RedisSegmentCache, RedisSplitCache)
from django_splitio.tests.utils import redis


class SingletonsTests(TestCase):
    def test_segment_cache_built_with_settings_redis_factory(self):
        """Tests that the segment_cache singleton was built with the result of calling the redis
        factory"""
        self.assertEqual(redis, segment_cache._redis)

    def test_split_cache_built_with_settings_redis_factory(self):
        """Tests that the split_cache singleton was built with the result of calling the redis
        factory"""
        self.assertEqual(redis, split_cache._redis)

    def test_impressions_cache_built_with_settings_redis_factory(self):
        """Tests that the impressions_cache singleton was built with the result of calling the redis
        factory"""
        self.assertEqual(redis, impressions_cache._redis)

    def test_metrics_cache_built_with_settings_redis_factory(self):
        """Tests that the metrics_cache singleton was built with the result of calling the redis
        factory"""
        self.assertEqual(redis, metrics_cache._redis)


class RedisSegmentCacheTests(TestCase):
    def setUp(self):
        self.some_segment_name = mock.MagicMock()
        self.some_segment_name_str = 'some_segment_name'
        self.some_segment_keys = [mock.MagicMock(), mock.MagicMock()]
        self.some_key = mock.MagicMock()
        self.some_change_number = mock.MagicMock()
        self.some_redis = mock.MagicMock()
        self.a_segment_cache = RedisSegmentCache(self.some_redis)

    def test_disable_sets_disabled_key(self):
        """Test that disable sets the disabled key for segments"""
        self.a_segment_cache.disable()
        self.some_redis.set.assert_called_once_with('SPLITIO.segments.__disabled__', 1)

    def test_enable_deletes_disabled_key(self):
        """Test that enable deletes the disabled key for segments"""
        self.a_segment_cache.enable()
        self.some_redis.delete.assert_called_once_with('SPLITIO.segments.__disabled__')

    def test_is_enabled_returns_false_if_disabled_key_exists(self):
        """Test that is_enabled returns False if disabled key exists"""
        self.some_redis.exists.return_value = True
        self.assertFalse(self.a_segment_cache.is_enabled())
        self.some_redis.exists.assert_called_once_with('SPLITIO.segments.__disabled__')

    def test_is_enabled_returns_true_if_disabled_key_doesnt_exist(self):
        """Test that is_enabled returns True if disabled key doesn't exist"""
        self.some_redis.exists.return_value = False
        self.assertTrue(self.a_segment_cache.is_enabled())
        self.some_redis.exists.assert_called_once_with('SPLITIO.segments.__disabled__')

    def test_register_segment_adds_segment_name_to_register_segments_set(self):
        """Test that register_segment adds segment name to registered segments set"""
        self.a_segment_cache.register_segment(self.some_segment_name)
        self.some_redis.sadd.assert_called_once_with('SPLITIO.segments.__registered_segments__',
                                                     self.some_segment_name)

    def test_unregister_segment_removes_segment_name_to_register_segments_set(self):
        """Test that unregister_segment removes segment name to registered segments set"""
        self.a_segment_cache.unregister_segment(self.some_segment_name)
        self.some_redis.srem.assert_called_once_with('SPLITIO.segments.__registered_segments__',
                                                     self.some_segment_name)

    def test_get_registered_segments_returns_registered_segments_set_members(self):
        """Test that get_registered_segments returns the registered segments sets members"""
        self.assertEqual(self.some_redis.smembers.return_value,
                         self.a_segment_cache.get_registered_segments())
        self.some_redis.smembers.assert_called_once_with('SPLITIO.segments.__registered_segments__')

    def test_add_keys_to_segment_adds_keys_to_segment_set(self):
        """Test that add_keys_to_segment adds the keys to the segment key set"""
        self.a_segment_cache.add_keys_to_segment(self.some_segment_name_str, self.some_segment_keys)
        self.some_redis.sadd.assert_called_once_with(
            'SPLITIO.segments.segment.some_segment_name.key_set', self.some_segment_keys[0],
            self.some_segment_keys[1])

    def test_remove_keys_from_segment_remove_keys_from_segment_set(self):
        """Test that remove_keys_from_segment removes the keys to the segment key set"""
        self.a_segment_cache.remove_keys_from_segment(self.some_segment_name_str, self.some_segment_keys)
        self.some_redis.srem.assert_called_once_with(
            'SPLITIO.segments.segment.some_segment_name.key_set', self.some_segment_keys[0],
            self.some_segment_keys[1])

    def test_is_in_segment_tests_whether_a_key_is_in_a_segments_key_set(self):
        """Test that is_in_segment checks if a key is in a segment's key set"""
        self.assertEqual(self.some_redis.sismember.return_value,
                         self.a_segment_cache.is_in_segment(self.some_segment_name_str,
                                                            self.some_key))
        self.some_redis.sismember.assert_called_once_with(
            'SPLITIO.segments.segment.some_segment_name.key_set', self.some_key)

    def test_set_change_number_sets_segment_change_number_key(self):
        """Test that set_change_number sets the segment's change number key"""
        self.a_segment_cache.set_change_number(self.some_segment_name_str, self.some_change_number)
        self.some_redis.set.assert_called_once_with(
            'SPLITIO.segments.segment.some_segment_name.change_number', self.some_change_number)

    def test_get_change_number_gets_segment_change_number_key(self):
        """Test that get_change_number gets the segment's change number key"""
        self.assertEqual(self.some_redis.get.return_value,
                         self.a_segment_cache.get_change_number(self.some_segment_name_str))
        self.some_redis.get.assert_called_once_with(
            'SPLITIO.segments.segment.some_segment_name.change_number')

    def test_get_change_number_returns_default_value_if_not_set(self):
        """Test that get_change_number returns -1 if the value is not set"""
        self.some_redis.get.return_value = None
        self.assertEqual(-1,
                         self.a_segment_cache.get_change_number(self.some_segment_name_str))


class RedisSplitCacheTests(TestCase, MockUtilsMixin):
    def setUp(self):
        self.pickle_mock = self.patch('django_splitio.cache.pickle')
        self.some_split_name = mock.MagicMock()
        self.some_split_name_str = 'some_split_name'
        self.some_split = mock.MagicMock()
        self.some_change_number = mock.MagicMock()
        self.some_redis = mock.MagicMock()
        self.a_split_cache = RedisSplitCache(self.some_redis)

    def test_disable_sets_disabled_key(self):
        """Test that disable sets the disabled key for splits"""
        self.a_split_cache.disable()
        self.some_redis.set.assert_called_once_with('SPLITIO.splits.__disabled__', 1)

    def test_enable_deletes_disabled_key(self):
        """Test that enable deletes the disabled key for splits"""
        self.a_split_cache.enable()
        self.some_redis.delete.assert_called_once_with('SPLITIO.splits.__disabled__')

    def test_is_enabled_returns_false_if_disabled_key_exists(self):
        """Test that is_enabled returns False if disabled key exists"""
        self.some_redis.exists.return_value = True
        self.assertFalse(self.a_split_cache.is_enabled())
        self.some_redis.exists.assert_called_once_with('SPLITIO.splits.__disabled__')

    def test_is_enabled_returns_true_if_disabled_key_doesnt_exist(self):
        """Test that is_enabled returns True if disabled key doesn't exist"""
        self.some_redis.exists.return_value = False
        self.assertTrue(self.a_split_cache.is_enabled())
        self.some_redis.exists.assert_called_once_with('SPLITIO.splits.__disabled__')

    def test_set_change_number_sets_change_number_key(self):
        """Test that set_change_number sets the change number key"""
        self.a_split_cache.set_change_number(self.some_change_number)
        self.some_redis.set.assert_called_once_with(
            'SPLITIO.splits.__change_number__', self.some_change_number, None)

    def test_get_change_number_gets_segment_change_number_key(self):
        """Test that get_change_number gets the change number key"""
        self.assertEqual(self.some_redis.get.return_value,
                         self.a_split_cache.get_change_number())
        self.some_redis.get.assert_called_once_with(
            'SPLITIO.splits.__change_number__')

    def test_get_change_number_returns_default_value_if_not_set(self):
        """Test that get_change_number returns -1 if the value is not set"""
        self.some_redis.get.return_value = None
        self.assertEqual(-1, self.a_split_cache.get_change_number())

    def test_add_split_sets_split_key_with_pickled_split(self):
        """Test that add_split sets the split key with pickled split"""
        self.a_split_cache.add_split(self.some_split_name_str, self.some_split)
        self.pickle_mock.dumps.assert_called_once_with(self.some_split)
        self.some_redis.set.assert_called_once_with('SPLITIO.splits.some_split_name',
                                                    self.pickle_mock.dumps.return_value)

    def test_get_split_returns_unpickled_cached_split(self):
        """Test that if a split is cached get_split returns its unpickled form"""
        self.assertEqual(self.pickle_mock.loads.return_value,
                         self.a_split_cache.get_split(self.some_split_name_str))
        self.some_redis.get.assert_called_once_with('SPLITIO.splits.some_split_name')
        self.pickle_mock.loads.assert_called_once_with(self.some_redis.get.return_value)

    def test_get_split_returns_none_if_not_cached(self):
        """Test that if a split is not cached get_split returns None"""
        self.some_redis.get.return_value = None
        self.assertEqual(None, self.a_split_cache.get_split(self.some_split_name_str))
        self.some_redis.get.assert_called_once_with('SPLITIO.splits.some_split_name')

    def test_remove_split_deletes_split_key(self):
        """Test that remove_split deletes the split key"""
        self.a_split_cache.remove_split(self.some_split_name_str)
        self.some_redis.delete.assert_called_once_with('SPLITIO.splits.some_split_name')
