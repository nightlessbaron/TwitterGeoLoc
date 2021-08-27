"""Main location resolution classes and methods."""


from abc import ABCMeta, abstractmethod
import json, os
import pkgutil
import tweepy
from .location import Location, EARTH
from itertools import groupby
import spacy
from spacy import displacy
import en_core_web_sm

import warnings

ABC = ABCMeta('ABC', (object,), {}) # compatible with Python 2 *and* 3 
meta_path = 'C:/Users/Varad/OneDrive/Desktop/pennhlp/metadata/'
user_dict, user_bio_dict = {}, {}

# My APP keys
consumer_key = "SrIEfX9ImqclVQ82Ua3CMEOLo"
consumer_secret = "WVFjRx75ktPOxV1URvTASqw4NR91OlNlzq76gCREpIIGj9CgUu"
access_token = "1353238046074925056-9g2KhPCjo4Qk9DPw825ChYXpRWRsW6"
access_secret_token = "YbNfbOKhKjiM15tJ8MGHXp6S6Ttk4qpGAU64HakO24E8R"

# Authenticating my keys and setting up API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret_token)
api = tweepy.API(auth, wait_on_rate_limit=True)

class AbstractResolver(ABC):
    """An abstract base class for *resolvers* that match tweets to known
    locations."""
    location_id_to_location = {}
    @abstractmethod
    def add_location(self, location):
        """Add an individual :py:class:`.Location` object to this
        resolver's set of known locations."""
        pass

    def load_locations(self, location_file=None):
        """Load locations into this resolver from the given
        *location_file*, which should contain one JSON object per line
        representing a location.  If *location_file* is not specified,
        an internal location database is used."""
        if location_file is None:
            #contents = pkgutil.get_data(__package__, 'data/locations.json')
            contents = pkgutil.get_data(__package__, 'data/locations_error_resolved_v3.json')
            contents_string = contents.decode("utf-8")
            locations = contents_string.split('\n')
        else:
            from .cli import open_file
            with open_file(location_file, 'rb') as input:
                locations = input.readlines()
        
        for location_string in locations:
            if location_string.strip():
                location = Location(known=True, **json.loads(location_string))
                self.location_id_to_location[location.id] = location
                self.add_location(location)

    @abstractmethod
    def resolve_tweet(self, tweet):
        """Find the best known location for the given *tweet*, which is
        provided as a deserialized JSON object, and return a tuple
        containing two elements: a boolean indicating whether the
        resolution is *provisional*, and a :py:class:`.Location` object.
        Provisional resolutions may be overridden by non-provisional
        resolutions returned by a less preferred resolver (i.e., one
        that comes later in the resolver order), and should be used when
        returning locations with low confidence, such as those found by
        using larger "backed-off" administrative units.

        If no suitable locations are found, ``None`` may be returned.
        """
        pass

    def get_location_by_id(self, location_id):
        return self.location_id_to_location[location_id]


class ResolverCollection(AbstractResolver):
    """A "supervising" resolver that attempts to resolve a tweet's
    location by using multiple child resolvers and returning the
    resolution with the highest priority."""

    def __init__(self, resolvers=None):
        self.resolvers = resolvers if resolvers else []
        self.add_location(EARTH)


    def add_location(self, location):
        # Inform our child resolvers of this location.
        for resolver_name, resolver in self.resolvers:
            resolver.add_location(location)

    def bio_resolution(self, tweet):
        user_name = tweet.get('user', {}).get('screen_name', '')
        if user_name not in user_bio_dict:
            user_bio = tweet.get('user', {}).get('description', '')
            location_list = []
            nlp = en_core_web_sm.load()
            warnings.simplefilter("ignore", ResourceWarning) # can be removed after release of next version of spacy
            article = nlp(user_bio)
            for x in article.ents:
                if x.label_ == "GPE":
                    location = x.text
                    resolution = resolver.resolve_tweet(location)
                    if resolution != None:
                        location_list.append(resolution)
            flag_dict = {}
            for i in range(len(location_list)):
                if location_list[i][1].get('city', '') != '':
                    flag_dict['city'] = i
                elif location_list[i][1].get('county', '') != '':
                    flag_dict['county'] = i
                elif location_list[i][1].get('state', '') != '':
                    flag_dict['state'] = i
                else:
                    flag_dict['country'] = i
            for key in ['city', 'county', 'state', 'country']:
                if flag_dict[key] >= 0:
                    resolution = location_list[flag_dict[key]]
                    break
            else:
                resolution = resolver.resolve_tweet(tweet)
            user_bio_dict[user_name] = resolution
        else:
            resolution = user_bio_dict[user_name]
        return resolution

    def save_to_disk(self, resolver, user_name, tweet, disk=False):
        try:
        # Saving timelines to disk
            resolution_list = []
            if os.path.exists(meta_path+user_name+'.json'): # Timeline exists on disk
                with open(meta_path+user_name+'.json', 'r') as fmeta:
                    user_tweets = [line for line in json.load(fmeta)]
            else:
                user_tweets = api.user_timeline(user_name, count=100)
                for itr in range(len(user_tweets)):
                    user_tweets[itr] = user_tweets[itr]._json
                if disk == True:
                    with open(meta_path+user_name+'.json', 'a') as fmeta:
                        json.dump(user_tweets, fmeta)
            for tweety in user_tweets:
                resolution = resolver.resolve_tweet(tweety)
                if resolution != None:
                    resolution_list.append(resolution)
            resolution_dict = {value: len(list(freq)) for value, freq in groupby(sorted(resolution_list))}
            if resolution_dict == {}:
                resolution = None
            else:
                resolution = max(resolution_dict)
        except Exception as e:
            print(e, user_name)
            resolution = resolver.resolve_tweet(tweet)
        return resolution

    def user_aggregation(self, resolver_name, resolver, tweet):
        if resolver_name not in ['contentplus', 'bioplus']:
            user_name = tweet.get('user', {}).get('screen_name', '')
            if user_name != '':# and user_name not in ['JTrussell','blueduckie24']:
                if user_name not in user_dict:
                    resolution = self.save_to_disk(resolver, user_name, tweet, True) # Need to change True to variable
                    user_dict[user_name] = resolution
                else:
                    resolution = resolver.resolve_tweet(tweet)
                    if resolution is None:
                        resolution = user_dict[user_name]
            else:
                #if user_name == 'JTrussell':
                #    resolution = (False, Location(country='United States', state='Missouri', known=True, id=4398678, population=5768151))
                #elif user_name == 'blueduckie24':
                #    resolution = (False, Location(country='United States', state='New York', known=True, id=5128638, population=19274244))
                #else:
                resolution = resolver.resolve_tweet(tweet)
        elif resolver_name == 'bioplus':
            resolution = self.bio_resolution(tweet)
        else:
            resolution = resolver.resolve_tweet(tweet)
        return resolution

    def resolve_tweet(self, tweet):
        provisional_resolution = None
        for resolver_name, resolver in self.resolvers:
            # Addding user tweet aggregation here.
            user_agg = False # Need to replace it! Change to a variable
            if user_agg == True:
                resolution = self.user_aggregation(resolver_name, resolver, tweet)
            else:
                resolution = resolver.resolve_tweet(tweet)

            if resolution is None:
                continue
            is_provisional, location = resolution
            location.resolution_method = resolver_name
            # If we only got a provisional resolution, hold on to it
            # as long as we don't already have a more preferred one,
            # and see if we get a non-provisional one later.
            if is_provisional:
                if provisional_resolution is None:
                    provisional_resolution = resolution
            else:
                return resolution
        # We didn't find any non-provisional resolutions; return the
        # best provisional resolution.  This will be None if we didn't
        # find any provisional resolutions, either.
        return provisional_resolution


### Resolver importation functions.
#
known_resolvers = {}


def register(name):
    """Return a decorator that registers the decorated class as a
    resolver with the given *name*."""
    def decorator(class_):
        if name in known_resolvers:
            raise ValueError('duplicate resolver name "%s"' % name)
        known_resolvers[name] = class_
    return decorator


def get_resolver(order=None, options=None, modules=None):
    """Return a location resolver.  The *order* argument, if given,
    should be a list of resolver names; results from resolvers named
    earlier in the list are preferred over later ones.  For a list of
    built-in resolver names, see :doc:`/resolvers`.  The *options*
    argument can be used to pass configuration options to individual
    resolvers, in the form of a dictionary mapping resolver names to
    keyword arguments::

        {'geocode': {'max_distance': 50}}

    The *modules* argument can be used to specify a list of additional
    modules to look for resolvers in.  See :doc:`/develop` for details.
    """
    #print("Initial known_resolvers", known_resolvers)
    if not known_resolvers:
        from . import resolvers as carmen_resolvers
        modules = [carmen_resolvers] + (modules or []) # Returns [] is modules is None otherwise return modules.
        for module in modules: # The following line of code automatically imports the subpackages in the main 
                               # package. pkgutil is a tool for module discovery
            for loader, name, _ in pkgutil.iter_modules(module.__path__):
                full_name = module.__name__ + '.' + name
                #print("These are modules:", full_name)
                loader.find_module(full_name).load_module(full_name)
        #print("Final known_resolvers", known_resolvers) # Maybe have a look at the function at Line 105 in the same
                                                        # document.
    if order is None:
        #order = ('place', 'geocode', 'profileplus', 'contentplus') # Default order
        order = ('geoname', 'place', 'profileplus')
    else:
        order = tuple(order)
    if options is None:
        options = {} # default setting for resolvers
    resolvers = []
    for resolver_name in order:
        if resolver_name not in known_resolvers:  # checks if the resolver is from the 3 known resolvers or not.
                                                  # checked, it is.
            raise ValueError('unknown resolver name "%s"' % resolver_name)
        resolvers.append((
            resolver_name,
            known_resolvers[resolver_name](**options.get(resolver_name, {}))))
    #print("Let's check how it looks before feeding to the main class:", resolvers)
    return ResolverCollection(resolvers)
