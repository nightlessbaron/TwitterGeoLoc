#!/usr/bin/env python
from __future__ import print_function

import argparse
import collections
import gzip
import json, csv
import sys
import warnings
import os
import ast

from . import get_resolver
from .location import Location, LocationEncoder

def parse_args():
    parser = argparse.ArgumentParser(
        description='Resolve tweet locations.',
        epilog='Paths ending in ".gz" are treated as gzipped files.')
    parser.add_argument('-s', '--statistics',
        action='store_true',
        help='show summary statistics')
    parser.add_argument('--order',
        metavar='RESOLVERS',  # Metavar helps in displaying the value in argspace option command.
        help='preferred resolver order (comma-separated)')
    parser.add_argument('--options',
        default='{}',
        help='JSON dictionary of resolver options')
    parser.add_argument('--locations',
        metavar='PATH', dest='location_file',
        help='path to alternative location database')
    parser.add_argument('input_file', metavar='input_path',
        nargs='?', default=sys.stdin,
        help='file containing tweets to locate with geolocation field '
             '(defaults to standard input)')
    parser.add_argument('output_file', metavar='output_path',
        nargs='?', default=sys.stdout,
        help='file to write geolocated tweets to (defaults to standard '
             'output)')
    return parser.parse_args()


def open_file(filename, mode):
    if filename.endswith('.gz'):
        return gzip.open(filename, mode)
    else:
        return open(filename, mode)


def main():
    args = parse_args()
    warnings.simplefilter('always') # Causes all warnings to be always triggered.
    resolver_kwargs = {}
    if args.order is not None: # args.order gives an order in which resolvers are triggered
        resolver_kwargs['order'] = args.order.split(',') # order argument is a list of resolver names.
    if args.options is not None:                         # ['geocode', 'place', 'profile']
        #resolver_kwargs['options'] = json.loads(args.options) # json dictionary of resolver options. 
        resolver_kwargs['options'] = ast.literal_eval(args.options)
    #print(resolver_kwargs['options'])
    # For example, {'geocode': {'max_distance' : 50}}
    #print(resolver_kwargs)
    #resolver_kwargs['country'] = args.country
    resolver = get_resolver(**resolver_kwargs) # This returns a location resolver.
    #print("This is the resolver:", resolver.resolvers) # Resolvers : {geocode, profile, place}
    # Now, we can extract the individual resolvers.
    #print("This one is geocode:", resolver.resolvers[0]) # Returns a resolver along with its place object

    resolver.load_locations(location_file=args.location_file)
    # Variables for statistics.
    city_found = county_found = state_found = country_found = 0
    has_place = has_coordinates = has_geo = has_profile_location = has_content = 0
    resolution_method_counts = collections.defaultdict(int)
    skipped_tweets = resolved_tweets = total_tweets = 0
    
    with open_file(args.input_file, 'rb') as input_file, open_file(args.output_file, 'wb') as output_file:#, open('analysis.csv', 'a') as file:
        #file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i, input_line in enumerate(input_file):
            # Show warnings from the input file, not the Python source code.
            def showwarning(message, category, filename, lineno,
                            file=sys.stderr, line=None):
                sys.stderr.write(warnings.formatwarning(
                    message, category, input_file.name, i+1,
                    line=''))
            warnings.showwarning = showwarning
            try:
                if len(input_line.strip()) == 0:
                    continue
                tweet = json.loads(input_line)
            except ValueError:
                warnings.warn('Invalid JSON object')
                skipped_tweets += 1
                continue
            # Collect statistics on the tweet.
            if tweet.get('place'):
                has_place += 1
            elif tweet.get('coordinates'):
                has_coordinates += 1
            elif tweet.get('geo'):
                has_geo += 1
            elif tweet.get('user', {}).get('location', ''):
                has_profile_location += 1
            else:
                try:
                    if tweet.get('text', ''):
                        has_content += 1
                except:
                    if tweet.get('retweeted_status', {}).get('text', ''):
                        has_content +=  1
            # Perform the actual resolution.
            resolution = resolver.resolve_tweet(tweet)
            if resolution:
                location = resolution[1]
                tweet['location'] = location
                # More statistics.
                resolution_method_counts[location.resolution_method] += 1
                # Adding location analysis report 
                #file_writer.writerow([str(i), str(location)])
                user_name = tweet.get('user',{}).get('screen_name', '')
                #with open('analysis.txt', 'a') as ff:
                #    ff.write(str(i) + '\t' + user_name + '\t' + str(location) + '\n')
                #print(i, location)
                if location.city:
                    city_found += 1
                    #print(location.city)
                elif location.county:
                    county_found += 1
                    #print(location.county)
                elif location.state:
                    state_found += 1
                    #print(location.state)
                elif location.country:
                    country_found += 1
                    #print(location.country)
                resolved_tweets += 1
            json_output = json.dumps(tweet, cls=LocationEncoder).encode()
            output_file.write(json_output)
            output_file.write(bytes('\n'.encode(encoding='ascii')))
            total_tweets += 1
        
    if args.statistics:
        print('Skipped %d tweets.' % skipped_tweets, file=sys.stderr)
        print('Tweets with "place" key: %d; '
                                       '"coordinates" key: %d; '
                                       '"geo" key: %d.' % (
                                        has_place, has_coordinates, has_geo), file=sys.stderr)
        print('Resolved %d tweets to a city, '
                                       '%d to a county, %d to a state, '
                                       'and %d to a country.' % (
                                city_found, county_found,
                                state_found, country_found), file=sys.stderr)
        print('Tweet resolution methods: %s.' % (
            ', '.join('%d by %s' % (v, k)
                for (k, v) in resolution_method_counts.items())), file=sys.stderr)
    print('Resolved locations for %d of %d tweets.' % (
        resolved_tweets, total_tweets), file=sys.stderr)


if __name__ == '__main__':
    try:
        #os.remove('analysis.txt')
        #os.remove('analysis_locations.txt')
        main()
    except:
        main()
