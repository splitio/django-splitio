from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from splitio.splits import SplitParser, Status, ApiSplitChangeFetcher, CacheBasedSplitFetcher
from splitio.segments import ApiSegmentChangeFetcher, CacheBasedSegment, CacheBasedSegmentFetcher

from .api import sdk_api
from .cache import segment_cache, split_cache

_logger = logging.getLogger(__name__)


def update_segments(a_segment_cache, a_segment_change_fetcher):
    """If updates are enabled, this function updates all the segments listed by the segment cache
    get_registered_segments() method making requests to the Split.io SDK API. If an exception is
    raised, the process is stopped and it won't try to update segments again until enabled_updates
    is called on the segment cache."""
    try:
        if not a_segment_cache.is_enabled():
            return

        registered_segments = a_segment_cache.get_registered_segments()
        for name in registered_segments:
            update_segment(a_segment_cache, name, a_segment_change_fetcher)
    except:
        _logger.exception('Exception caught updating segment definitions')
        a_segment_cache.disable()


def update_segment(a_segment_cache, segment_name, a_segment_change_fetcher):
    """Updates a segment. It will eagerly request all changes until the change number is the same
    "till" value in the response.
    :param segment_name: The name of the segment
    :type segment_name: str
    """
    till = a_segment_cache.get_change_number(segment_name)

    while True:
        response = a_segment_change_fetcher.fetch(segment_name, till)

        if till >= response['till']:
            return

        if len(response['removed']) > 0:
            a_segment_cache.remove_keys_from_segment(segment_name, response['removed'])

        if len(response['added']) > 0:
            a_segment_cache.add_keys_to_segment(segment_name, response['added'])

        a_segment_cache.set_change_number(segment_name, response['till'])

        till = response['till']


class RedisSplitParser(SplitParser):
    def __init__(self, a_segment_fetcher, a_some_segment_cache):
        """
        A SplitParser implementation that registers the segments with the redis segment cache
        implementation upon parsing an IN_SEGMENT matcher.
        :param a_segment_fetcher: The segment fetcher
        :type a_segment_fetcher: SegmentFetcher
        :param a_some_segment_cache: The segment cache
        :type a_some_segment_cache: RedisSegmentCache
        """
        super(RedisSplitParser, self).__init__(a_segment_fetcher)
        self._segment_cache = a_some_segment_cache

    def _parse_matcher_in_segment(self, matcher, *args, **kwargs):
        delegate = super(RedisSplitParser, self)._parse_matcher_in_segment(matcher, *args, **kwargs)
        self._segment_cache.register_segment(delegate.segment.name)
        return delegate


def update_splits(a_split_cache, a_split_change_fetcher, a_split_parser):
    """If updates are enabled, this function updates (or initializes) the current cached split
    configuration. It can be called by periodic update tasks or directly to force an unscheduled
    update. If an exception is raised, the process is stopped and it won't try to update splits
    again until enabled_updates is called on the splits cache.
    """
    try:
        if not a_split_cache.is_enabled():
            return

        till = a_split_cache.get_change_number()

        while True:
            response = a_split_change_fetcher.fetch(till)

            if till >= response['till']:
                return

            if 'splits' in response and len(response['splits']) > 0:
                added_features = []
                removed_features = []

                for split_change in response['splits']:
                    if Status(split_change['status']) != Status.ACTIVE:
                        a_split_cache.remove_split(split_change['name'])
                        continue

                    parsed_split = a_split_parser.parse(split_change)
                    if parsed_split is None:
                        _logger.warning(
                            'We could not parse the split definition for %s. '
                            'Removing split to be safe.', split_change['name'])
                        a_split_cache.remove_split(split_change['name'])
                        removed_features.append(split_change['name'])
                        continue

                    added_features.append(split_change['name'])
                    a_split_cache.add_split(split_change['name'], parsed_split)

                if len(added_features) > 0:
                    _logger.info('Updated features: %s', added_features)

                if len(removed_features) > 0:
                    _logger.info('Deleted features: %s', removed_features)

            till = response['till']
            a_split_cache.set_change_number(response['till'])
    except:
        _logger.exception('Exception caught updating split definitions')
        a_split_cache.disable()


class RedisBasedSegment(CacheBasedSegment):
    def __init__(self, name):
        """A CacheBasedSegment used for pickling/unpickling segments removing and setting the reference
        to the local segment_cache instance.
        :param name: The name of the segment
        :type name: str
        """
        super(RedisBasedSegment, self).__init__(name, segment_cache)
    
    def __getstate__(self):
        old_dict = self.__dict__.copy()
        del old_dict['_segment_cache']
        return old_dict

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self._segment_cache = segment_cache


class RedisSegmentFetcher(CacheBasedSegmentFetcher):
    def fetch(self, name, block_until_ready=False):
        """
        Fetch cache based segment
        :param name: The name of the segment
        :type name: str
        :param block_until_ready: Whether to wait until all the data is available
        :type block_until_ready: bool
        :return: A segment for the given name
        :rtype: Segment
        """
        segment = RedisBasedSegment(name)
        return segment

segment_change_fetcher = ApiSegmentChangeFetcher(sdk_api)
segment_fetcher = RedisSegmentFetcher(segment_cache)
split_parser = RedisSplitParser(segment_fetcher, segment_cache)
split_change_fetcher = ApiSplitChangeFetcher(sdk_api)
split_fetcher = CacheBasedSplitFetcher(split_cache)
