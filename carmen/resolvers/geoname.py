"""Resolvers based on Twitter user geoname data."""


import re
import json
import warnings

from ..names import *
from ..resolver import AbstractResolver, register

@register('geoname')
class GeonameResolver(AbstractResolver):
    """A resolver that locates a tweet by matching the tweet author's
    geoname location against known locations."""

    name = 'geoname'

    def __init__(self):
        self.geoid_to_location = {}
        self.tweetid_to_geoid = {}
        self.add_id_table()

    def add_id_table(self):
        """Load tweet_id into this resolver from the given
        *json_file*, which should contain one JSON object per line
        representing a tweet_id and geoname equivalent."""
        with open('carmen/data/on_record.json') as json_file:
            table = json.load(json_file)
            for row in table:
                self.tweetid_to_geoid.update(row)

    def add_location(self, location):
        geoid = location.id
        self.geoid_to_location[str(geoid)] = location

    def resolve_tweet(self, tweet):
        if tweet['place'] == None:
            return None

        tweet_id = tweet.get('place', {}).get('id', '')
            
        if tweet_id == '':
            return None

        geoid, city, state, country = self.tweetid_to_geoid.get(tweet_id, ['','','',''])
        if geoid == '':
            print(tweet_id, 'is not present in database. Recommended to add it')
            # TO-DD
            # Return an approximate location by searching through the location database.
            return None
        if self.geoid_to_location.get(geoid, '') == '':
            print(geoid, 'is missing from location database.')
            # TO-DO
            # Add the respective geoname id information in database.
            return None
        return (False, self.geoid_to_location[geoid])