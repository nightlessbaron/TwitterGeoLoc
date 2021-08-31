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
        self.tweets_included = {}
        self.geoid_included = {}
        self.add_id_table()
        self.add_tweets()
        self.add_geoid()

    def add_tweets(self):
        with open('missing_tweet_id.json', 'r') as mtir:
            for line in mtir.readlines():
                json_line = json.loads(line)
                self.tweets_included.update(json_line)

    def add_geoid(self):
        with open('missing_geoname_id.json', 'r') as mgir:
            for line in mgir.readlines():
                json_line = json.loads(line)
                self.geoid_included.update(json_line)

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
        try:
            if tweet['place'] == None:
                return None
        except:
            return None # Deleted tweet with no information

        tweet_id = tweet.get('place', {}).get('id', '')
            
        if tweet_id == '':
            return None

        geoid, city, state, country = self.tweetid_to_geoid.get(tweet_id, ['','','',''])
        if geoid == '':
            if tweet_id not in self.tweets_included:
                self.tweets_included[tweet_id] = self.tweetid_to_geoid[tweet_id]
                with open('missing_tweet_id.json', 'a') as mti:
                    json.dump({tweet_id: self.tweetid_to_geoid[tweet_id]}, mti)
                    mti.write('\n')
            # TO-DD
            # Return an approximate location by searching through the location database.
            return None
        if self.geoid_to_location.get(geoid, '') == '':
            if geoid not in self.geoid_included:
                self.geoid_included[geoid] = 1
                with open('missing_geoname_id.json', 'a') as mgi:
                    json.dump({geoid: 1}, mgi)
                    mgi.write('\n')
            else:
                self.geoid_included[geoid] += 1
            # TO-DO
            # Add the respective geoname id information in database.
            return None
        return (False, self.geoid_to_location[geoid])