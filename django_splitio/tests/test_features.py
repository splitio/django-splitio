from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock

from django.test import TestCase

from splitio.tests.utils import MockUtilsMixin

from django_splitio.features import update_segments, update_segment


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