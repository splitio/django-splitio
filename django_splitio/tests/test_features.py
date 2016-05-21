from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock

import pickle

from django.test import TestCase

from splitio.tests.utils import MockUtilsMixin

from django_splitio.cache import segment_cache, split_cache
from django_splitio.api import sdk_api
from django_splitio.features import (update_segments, update_segment, RedisSplitParser,
                                     update_splits, RedisBasedSegment, RedisSegmentFetcher,
                                     segment_change_fetcher, segment_fetcher, split_parser,
                                     split_change_fetcher, split_fetcher)


class SingletonsTests(TestCase):
    def test_segment_change_fetcher_built_with_sdk_api(self):
        """Tests that the segment_change_fetcher was constructed with sdk_api"""
        self.assertEqual(sdk_api, segment_change_fetcher._api)

    def test_segment_fetcher_built_with_segment_cache(self):
        """Tests that segment_fetcher was constructed with segment_cache"""
        self.assertEqual(segment_cache, segment_fetcher._segment_cache)

    def test_split_parser_built_with_segment_fetcher_segment_cache(self):
        """Tests that split_parser was constructed with segment_fetcher and segment_cache"""
        self.assertEqual(segment_cache, split_parser._segment_cache)
        self.assertEqual(segment_fetcher, split_parser._segment_fetcher)

    def test_split_change_fetcher_built_with_sdk_api(self):
        """Tests that the segment_change_fetcher was constructed with sdk_api"""
        self.assertEqual(sdk_api, split_change_fetcher._api)

    def test_split_change_fetcher_built_with_sdk_api(self):
        """Tests that the split_fetcher was constructed with split_cache"""
        self.assertEqual(split_cache, split_fetcher._split_cache)


class UpdateSegmentsTests(TestCase, MockUtilsMixin):
    def setUp(self):
        self.some_segments_cache = mock.MagicMock()
        self.some_segments_cache.is_enabled.return_value = True
        self.some_segment_change_fetcher = mock.MagicMock()
        self.update_segment_mock = self.patch('django_splitio.features.update_segment')

    def test_doesnt_call_update_segment_if_cache_is_disabled(self):
        """Test that update_segments doesn't call update_segment if the segment cache is disabled"""
        self.some_segments_cache.is_enabled.return_value = False
        update_segments(self.some_segments_cache, self.some_segment_change_fetcher)
        self.update_segment_mock.assert_not_called()

    def test_doesnt_call_update_segment_if_there_are_no_registered_segments(self):
        """Test that update_segments doesn't call update_segment there are no registered segments"""
        self.some_segments_cache.get_registered_segments.return_value = []
        update_segments(self.some_segments_cache, self.some_segment_change_fetcher)
        self.update_segment_mock.assert_not_called()

    def test_calls_update_segment_for_each_registered_segment(self):
        """Test that update_segments calls update_segment on each registered segment"""
        some_segment_name = mock.MagicMock()
        some_other_segment_name = mock.MagicMock()
        self.some_segments_cache.get_registered_segments.return_value = [some_segment_name,
                                                                         some_other_segment_name]
        update_segments(self.some_segments_cache, self.some_segment_change_fetcher)
        self.assertListEqual([mock.call(self.some_segments_cache, some_segment_name,
                                        self.some_segment_change_fetcher),
                              mock.call(self.some_segments_cache, some_other_segment_name,
                                        self.some_segment_change_fetcher)],
                             self.update_segment_mock.call_args_list)

    def test_disables_cache_if_update_segment_raises_exception(self):
        """Test that update_segments disables segment_cache if update segment raises an exception"""
        self.update_segment_mock.side_effect = Exception()
        self.some_segments_cache.get_registered_segments.return_value = [mock.MagicMock()]
        update_segments(self.some_segments_cache, self.some_segment_change_fetcher)
        self.some_segments_cache.disable.assert_called_once_with()


class UpdateSegmentTests(TestCase):
    def setUp(self):
        self.some_segment_cache = mock.MagicMock()
        self.some_segment_cache.get_change_number.return_value = -1
        self.some_segment_name = mock.MagicMock()
        self.some_segment_change_fetcher = mock.MagicMock()
        self.some_segment_change_fetcher.fetch.side_effect = [  # Two updates
            {
                'name': 'some_segment_name',
                'added': ['user_id_6'],
                'removed': ['user_id_1', 'user_id_2'],
                'since': -1,
                'till': 1
            },
            {
                'name': 'some_segment_name',
                'added': ['user_id_7'],
                'removed': ['user_id_4'],
                'since': 1,
                'till': 2
            },
            {
                'name': 'some_segment_name',
                'added': [],
                'removed': [],
                'since': 2,
                'till': 2
            }
        ]

    def test_calls_get_change_number(self):
        """Test update_segment calls get_change_number on the segment cache"""
        update_segment(self.some_segment_cache, self.some_segment_name,
                       self.some_segment_change_fetcher)
        self.some_segment_cache.get_change_number.assert_called_once_with(self.some_segment_name)

    def test_calls_segment_change_fetcher_fetch(self):
        """Test that update_segment calls segment_change_fetcher's fetch until change numbers
        match"""
        update_segment(self.some_segment_cache, self.some_segment_name,
                       self.some_segment_change_fetcher)
        self.assertListEqual([mock.call(self.some_segment_name, -1),
                              mock.call(self.some_segment_name, 1),
                              mock.call(self.some_segment_name, 2)],
                             self.some_segment_change_fetcher.fetch.call_args_list)

    def test_calls_remove_keys_from_segment_for_all_removed_keys(self):
        """Test update_segment calls remove_keys_from_segment for keys removed on each update"""
        update_segment(self.some_segment_cache, self.some_segment_name,
                       self.some_segment_change_fetcher)
        self.assertListEqual([mock.call(self.some_segment_name, ['user_id_1', 'user_id_2']),
                              mock.call(self.some_segment_name, ['user_id_4'])],
                             self.some_segment_cache.remove_keys_from_segment.call_args_list)

    def test_calls_add_keys_to_segment_for_all_added_keys(self):
        """Test update_segment calls add_keys_to_segment for keys added on each update"""
        update_segment(self.some_segment_cache, self.some_segment_name,
                       self.some_segment_change_fetcher)
        self.assertListEqual([mock.call(self.some_segment_name, 1),
                              mock.call(self.some_segment_name, 2)],
                             self.some_segment_cache.set_change_number.call_args_list)

    def test_calls_set_change_number_for_updates(self):
        """Test update_segment calls set_change_number on each update"""
        update_segment(self.some_segment_cache, self.some_segment_name,
                       self.some_segment_change_fetcher)
        self.assertListEqual([mock.call(self.some_segment_name, ['user_id_6']),
                              mock.call(self.some_segment_name, ['user_id_7'])],
                             self.some_segment_cache.add_keys_to_segment.call_args_list)


class RedisSplitParserTests(TestCase, MockUtilsMixin):
    def setUp(self):
        self.some_matcher = mock.MagicMock()
        self.some_segment_fetcher = mock.MagicMock()
        self.some_segment_cache = mock.MagicMock()
        self.split_parser = RedisSplitParser(self.some_segment_fetcher, self.some_segment_cache)
        self.parse_matcher_in_segment_mock = self.patch(
            'django_splitio.features.SplitParser._parse_matcher_in_segment')

    def test_parse_matcher_in_segment_calls_ancestor_implementation(self):
        """Test that _parse_matcher_in_segment calls super implementation"""
        self.split_parser._parse_matcher_in_segment(self.some_matcher)
        self.parse_matcher_in_segment_mock.assert_called_once_with(self.some_matcher)

    def test_parse_matcher_in_segment_registers_segment(self):
        """Test that _parse_matcher_in_segment registers parsed segment"""
        self.split_parser._parse_matcher_in_segment(self.some_matcher)
        self.some_segment_cache.register_segment(
            self.parse_matcher_in_segment_mock.return_value.segment.name)

    def test_parse_matcher_in_segment_returns_ancestor_implementation_result(self):
        """Test that _parse_matcher_in_segment returns the result of calling the ancestor
        implementation"""
        self.assertEqual(self.parse_matcher_in_segment_mock.return_value,
                         self.split_parser._parse_matcher_in_segment(self.some_matcher))


class UpdateSplitsTests(TestCase, MockUtilsMixin):
    def setUp(self):
        self.some_split_cache = mock.MagicMock()
        self.some_split_cache.get_change_number.return_value = -1
        self.some_split_parser = mock.MagicMock()
        self.parse_side_effect = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
        self.some_split_parser.parse.side_effect = self.parse_side_effect
        self.some_split_change_fetcher = mock.MagicMock()
        self.some_split_change_fetcher.fetch.side_effect = [
            {
                'till': 1,
                'splits': [
                    {
                        'status': 'ACTIVE',
                        'name': 'some_split'
                    },
                    {
                        'status': 'ACTIVE',
                        'name': 'some_other_split'
                    }
                ]
            },
            {
                'till': 2,
                'splits': [
                    {
                        'status': 'ACTIVE',
                        'name': 'some_split'
                    },
                    {
                        'status': 'ARCHIVED',
                        'name': 'some_other_split'
                    }
                ]
            },
            {
                'till': 2,
                'splits': []
            }
        ]

    def test_calls_get_change_number(self):
        """Test that update_splits calls get_change_number on the split cache"""
        update_splits(self.some_split_cache, self.some_split_change_fetcher, self.some_split_parser)
        self.some_split_cache.get_change_number.assert_called_once_with()

    def test_calls_split_change_fetcher_fetch(self):
        """Test that update_splits calls split_change_fetcher's fetch method until change numbers
        match"""
        update_splits(self.some_split_cache, self.some_split_change_fetcher, self.some_split_parser)
        self.assertListEqual([mock.call(-1), mock.call(1), mock.call(2)],
                             self.some_split_change_fetcher.fetch.call_args_list)

    def test_calls_split_parser_parse(self):
        """Test that update_split calls split_parser's parse method on all active splits on each
        update"""
        update_splits(self.some_split_cache, self.some_split_change_fetcher, self.some_split_parser)
        self.assertListEqual([mock.call({'status': 'ACTIVE', 'name': 'some_split'}),
                              mock.call({'status': 'ACTIVE', 'name': 'some_other_split'}),
                              mock.call({'status': 'ACTIVE', 'name': 'some_split'})],
                             self.some_split_parser.parse.call_args_list)

    def test_calls_remove_split(self):
        """Test that update_split calls split_cache's remove_split method on archived splits"""
        update_splits(self.some_split_cache, self.some_split_change_fetcher, self.some_split_parser)
        self.some_split_cache.remove_split.assert_called_once_with('some_other_split')

    def test_calls_add_split(self):
        """Test that update_split calls split_cache's add_split method on active splits"""
        update_splits(self.some_split_cache, self.some_split_change_fetcher, self.some_split_parser)
        self.assertListEqual([mock.call('some_split', self.parse_side_effect[0]),
                              mock.call('some_other_split', self.parse_side_effect[1]),
                              mock.call('some_split', self.parse_side_effect[2])],
                             self.some_split_cache.add_split.call_args_list)

    def test_calls_set_change_number(self):
        """Test that update_split calls set_change_number on every update"""
        update_splits(self.some_split_cache, self.some_split_change_fetcher, self.some_split_parser)
        self.assertListEqual([mock.call(1), mock.call(2)],
                             self.some_split_cache.set_change_number.call_args_list)

    def test_disables_cache_on_exception(self):
        """Test that update_split calls disable on the split_cache when an exception is raised"""
        self.some_split_change_fetcher.fetch.side_effect = Exception()
        update_splits(self.some_split_cache, self.some_split_change_fetcher, self.some_split_parser)
        self.some_split_cache.disable.assert_called_once_with()


class RedisBasedSegmentTests(TestCase):
    def setUp(self):
        self.some_name = 'some_name'
        self.segment = RedisBasedSegment(self.some_name)

    def test_is_possible_to_pickle(self):
        """Test that is possible to pickle a RedisBasedSegment"""
        try:
            pickle.dumps(self.segment)
        except:
            self.fail('An unexpected exception was raised')

    def test_sets_segment_cache_on_unpickle(self):
        """Test that segment_cache is set on the RedisBasedSegment objects when unpickled"""
        pickled_segment = pickle.dumps(self.segment)
        unpickled_segment = pickle.loads(pickled_segment)
        self.assertEqual(segment_cache, unpickled_segment._segment_cache)


class RedisSegmentFetcherTests(TestCase, MockUtilsMixin):
    def setUp(self):
        self.redis_based_segment_mock = self.patch('django_splitio.features.RedisBasedSegment')
        self.some_name = mock.MagicMock()
        self.some_segment_cache = mock.MagicMock()
        self.segment_fetcher = RedisSegmentFetcher(self.some_segment_cache)

    def test_fetch_returns_redis_based_segment(self):
        """Test that fetch returns a RedisBasedSegment"""
        self.assertEqual(self.redis_based_segment_mock.return_value,
                         self.segment_fetcher.fetch(self.some_name))
        self.redis_based_segment_mock.assert_called_once_with(self.some_name)
