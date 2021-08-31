#!/usr/bin/env python
from __future__ import print_function
import unidecode
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

def get_info(data):
    # ID, Place, User ID, Location, Description, Tweet
    if data.get('user', {}).get('description', None) != None:
        desc = unidecode.unidecode(data.get('user', {}).get('description', None)).replace('\n\n', '').replace('\n', '')
    else:
        desc = data.get('user', {}).get('description', None)
    tweet = unidecode.unidecode(data.get('text', '')).replace('\n\n', '').replace('\n', '')
    try:
        if data['place'] == None:
            return [data.get('id', None), None, data.get('user', {}).get('id', None), data.get('user', {}).get('location', None), desc, tweet]
    except:
        return [data['delete']['status']['id'], None, data['delete']['status']['user_id'], None, None, None]
    return [data.get('id', None), data.get('place', {}).get('full_name', None), data.get('user', {}).get('id', None), data.get('user', {}).get('location', None), desc, tweet]

def save_file_evaluate(itr, tweet, location, filename, demand=None):
    with open('evaluate_'+filename+'.csv', 'a', encoding='utf-8') as fg:
        # ID, Place, User ID, Location, resolved_place, method, Description, Tweet
        evaluate_data = get_info(tweet)
        ide, place, user_id, location_name, desc, content = evaluate_data
        resolved_place, method = None, None
        if location != None:
            resolved_place = location.city + ' ' + location.state + ' ' + location.country
            method = location.resolution_method
        ide = str(ide) if ide != None else 'None'
        place = 'None' if place == None else place
        user_id = str(user_id) if user_id != None else 'None'
        location_name = 'None' if location_name == None else location_name 
        resolved_place = 'None' if resolved_place == None else resolved_place
        method = 'None' if method == None else method
        desc = 'None' if desc == None else desc
        content = 'None' if content == None else content
        demand = method if demand == None else demand
        to_write = ide + ',' + place + ',' + user_id + ',' + location_name + ',' + \
        resolved_place + ',' + method + ',' + desc + ',' + content
        if itr == 0:
            fg.write('Id' + ',' + 'Place' + ',' + 'User ID' + ',' + 'Location' + ',' + 'Resolution'\
            + ',' + 'Method' + ',' + 'Description' + ',' + 'Tweet' + '\n')
        if itr < 200 and method == demand:
            fg.write(to_write + '\n')
            itr += 1
        return itr

def main():
    args = parse_args()
    warnings.simplefilter('always')
    resolver_kwargs = {}
    if args.order is not None:
        resolver_kwargs['order'] = args.order.split(',') 
    if args.options is not None:  
        resolver_kwargs['options'] = ast.literal_eval(args.options)
    resolver = get_resolver(**resolver_kwargs)

    resolver.load_locations(location_file=args.location_file)
    # Variables for statistics.
    city_found = county_found = state_found = country_found = 0
    has_place = has_coordinates = has_geo = has_profile_location = has_content = 0
    resolution_method_counts = collections.defaultdict(int)
    skipped_tweets = resolved_tweets = total_tweets = 0
    
    with open_file(args.input_file, 'rb') as input_file, open_file(args.output_file, 'wb') as output_file:
        itr, no_itr = 0, 0 # resolved, unresolved 
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
                user_name = tweet.get('user',{}).get('screen_name', '')
                if location.city:
                    city_found += 1
                elif location.county:
                    county_found += 1
                elif location.state:
                    state_found += 1
                elif location.country:
                    country_found += 1
                resolved_tweets += 1
                #itr = save_file_evaluate(tweet, location, 'geo', 'geoname')
                itr = save_file_evaluate(itr, tweet, location, 'resolved')
            else:
                no_itr = save_file_evaluate(no_itr, tweet, None, 'unresolved')
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
        main()
    except:
        main()
