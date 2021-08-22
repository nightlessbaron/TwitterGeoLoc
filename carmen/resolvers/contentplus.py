"""Resolvers based on Twitter user profile data."""


import re
import warnings
import fasttext
from ..names import *
from ..resolver import AbstractResolver, register

fasttext.FastText.eprint = lambda x: None # Suppresses warnings, can remove it after release of patch 0.9.3

model_path = 'C:/Users/Varad/OneDrive/Desktop/pennhlp/carmen/models/'


STATE_RE = re.compile(r'.+,\s*(\w+)')
NORMALIZATION_RE = re.compile(r'\s+|\W')
alias_dict = {}


def normalize(location_name, preserve_commas=False):
    """Normalize *location_name* by stripping punctuation and collapsing
    runs of whitespace, and return the normalized name."""
    def replace(match):
        if preserve_commas and ',' in match.group(0):
            return ','
        return ' '
    return NORMALIZATION_RE.sub(replace, location_name).strip().lower()


@register('contentplus')
class ContentPlusResolver(AbstractResolver):
    """A resolver that locates a tweet by matching the tweet author's
    profile location against known locations."""

    name = 'contentplus'

    def __init__(self, country='global'):
        self.location_name_to_location = {}
        self.country = country

    def add_location(self, location):
        aliases = list(location.aliases)
        aliases_already_added = set()
        for alias in aliases:
            if alias in aliases_already_added:
                continue
            if alias in self.location_name_to_location:
                if location.population > alias_dict[alias]:
                    self.location_name_to_location[alias] = location
                else:
                    continue
            else:
                self.location_name_to_location[alias] = location
                alias_dict[alias] = location.population
            # Additionally add a normalized version of the alias
            # stripped of punctuation, and with runs of whitespace
            # reduced to single spaces.
            normalized = normalize(alias)
            if normalized != alias:
                aliases.append(normalized)
            aliases_already_added.add(alias)

    def resolve_tweet(self, tweet):
        import sys
        try:
            user_tweet = tweet.get('text', '').replace('\n', ' ')
        except:
            user_tweet = tweet.get('retweeted_status', {}).get('text', '')

        location_string = ''
        if user_tweet != '':
            model = fasttext.load_model(model_path+'model_'+self.country+'.bin')
            location_string = model.predict(user_tweet)[0][0].replace('__label__', '')

        if not location_string:
            return None

        normalized = normalize(location_string)

        if normalized in self.location_name_to_location:
            return (False, self.location_name_to_location[normalized])
        # Try again with commas.
        normalized = normalize(location_string, preserve_commas=True)
        match = STATE_RE.search(normalized)
        if match:
            after_comma = match.group(1)
            location_name = None
            if after_comma in US_STATES or after_comma in COUNTRIES:
                location_name = after_comma
            elif after_comma in US_STATE_ABBREVIATIONS:
                location_name = US_STATE_ABBREVIATIONS[after_comma]
            elif after_comma in COUNTRY_CODES:
                location_name = COUNTRY_CODES[after_comma]
            if location_name in self.location_name_to_location:
                return (False, self.location_name_to_location[location_name])
        return None
