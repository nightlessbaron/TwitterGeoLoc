# TwitterGeoLoc: An easy to use GeoTagging Tool

## Introduction
`TwitterGeoLoc` is a python library for resolving geo locations of users on Twitter. It makes use of various instances of data present in a given tweet and the corresponding user's profile. Some of the instances taken into consideration in the current version of `TwitterGeoLoc` are:
- *Tweet Meta Data*: Coordinates of user or Place Tag assigned to the tweet.
- *Location Tag*: Location provided by user in tag present on user's profile.
- *User's Bio*: Users can mention their living location in the description space available on their profile.
- *Tweet content*: Mentions of a location name in a tweet.
The above four instances are ordered in a decreasing order of importance with the Tweet Metdata having the most precise information to tweet content having the least precise information. 

`TwitterGeoLoc` has been developed by keeping [carmen](https://github.com/mdredze/carmen-python/tree/v0.0.3) as a base and improving on the various drawbacks present in it. Some key features of `TwitterGeoLoc` are:
1. Lightweight and fast.
2. Comes with an improved location database.
3. Options available for using user aggregation.
4. Uses population heuristics to resolve locations with conflicts.
5. Allows to classify locations in tweet content country wise.
6. Possible to train new model and improve location database.
7. Performance benchmarked with other popular tools.
There's a lot of room for improving `TwitterGeoLoc`. Depending on how the system develops, we may consider seperating it from `carmen` and build our own API. We are happy to receive contributions. Please check the instructions in the **Contributions** Section for contributing.

## Installation and Quick Start

### Installation

The easiest way to install `TwitterGeoLoc` is cloning the GitHub repository. There are multiple ways to do it:
```shell
> git clone https://github.com/nightlessbaron/TwitterGeoLoc.git
```
or,
```shell
scoop update gh
gh repo clone nightlessbaron/TwitterGeoLoc
```
Otherwise, you can just download the `zip` and extract it. To load all the paths, you will need to change current path to the repository directory and do this:
```shell
pip install -e .
```

### Quick Start 

On a high level, `TwitterGeoLoc` can be used both from the terminal as well as a Python API. To use terminal, just execute the following line:
```shell
> python -m carmen.cli [options] [input_file] [output_file]
```
The input file should contain one JSON-serialized tweet per line, as returned by the Twitter API. If it is not specified, standard input is assumed. `TwitterGeoLoc` will output these tweets as JSON, with location information added in the `location key`, to the given output file, or standard output if none is specified. Both the input and output filenames may end in `.gz` to specify that Carmen should treat the files as gzipped text.

`[options]`: There are two options inbuilt in `TwitterGeoLoc` namely `-s (--statistics)` and `-h (--help)`.
* When `-s (--statistics)` is passed, `TwitterGeoLoc` will print a summary or statistics once the input file is resolved. It would print a summary of how many tweets were successfully resolved, and the resolution methods that were used to do so.
* You can make use of `-h (--help)` for getting any additional information about other options that can be passed to `TwitterGeoLoc`.

Similarly, `TwitterGeoLoc` can also be used as a Python API.
```python
import json
import carmen

tweet = json.loads(tweet_json)
resolver = carmen.get_resolver()
resolver.load_locations()
location = resolver.resolve_tweet(tweet)
```
You can check out more details regarding the resolvers and other functions in **Usage** and **Tutorials** sections.

## Directory Structure
The directory structure after installation and downloading the models should be:
```ascii
TwitterGeoLoc/
├─ carmen/
│  ├─ data/
│  │  ├─ gpkg_radius_all.tsv
│  │  ├─ locations.json
│  │  ├─ on_record.json
│  │  ├─ profile_locations_resolved.json
│  ├─ models/
│  │  ├─ model_brazil.bin
│  │  ├─ model_global.bin
│  │  ├─ ...
│  ├─ resolvers/
│  │  ├─ __init__.py
│  │  ├─ bioplus.py
│  │  ├─ contentplus.py
│  │  ├─ geocode.py
│  │  ├─ geoname.py
│  │  ├─ place.py
│  │  ├─ profile.py
│  │  ├─ profileplus.py
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ location.py
│  ├─ names.py
│  ├─ resolver.py
├─ dataset/
│  ├─ geotext.json
│  ├─ arxiv_geo.json
│  ├─ sample_dataset.json
├─ error-analysis/
│  ├─ analysis.csv
│  ├─ output.json
├─ metadata/
│  ├─ screen_name.json
│  ├─ ...
├─ .gitattributes
├─ README.md
├─ process_location_file.py
└─ experiments.py
```

## Usage

### Built-in Resolvers
Alongside the already three inbuilt resolvers in Carmen namely: `place`, `geocode`, and `profile` resolvers, we proposed a few more alternatives that are able to capture more finer details present in the user's tweet and profile.
To know about Carmen's pre-built resolvers in detail, please check their [docs](https://carmen.readthedocs.io/en/v0.0.3/resolvers.html)

1. `place` (carmen) resolver: Maps the twitter locations to known locations by name. If unresolved, it maps the unknown place or city, heirarchically to the known state or country name.
2. `geocode` (carmen) resolver:  Maps the location to the nearest known location using the coordinates of the unknown location. Uses `max_distance` option to restrict the search window of mapping the location.
3. `profile` (carmen) resolver: Maps the location present in the location field of user's profile to a known location name. Performance generally depends on how well the location search database captures information.
4. `geoname` (our) resolver: Maps the `id` present in `place` field to `geoname id`. This standardizes the location information and speeds up the search. Benchmark results show that it is able to capture location information more precisely than `place` resolver.
5. `profileplus` (our) resolver: Resolves unknown location to a known location by taking into consideration *Population Heuristics*, and compiling a rich location database. Thus, `profileplus` is able to capture more finer details as compared to `profile` resolver. Some popular locations are again mapped to their `geoname id`, hence resulting in increased performance.
6. `bioplus` (our) resolver: Extracts mentions of locations in description on user's profile using NER. Maps the unknown location to known location present in the location database. Aggregates on the multiple mentions of locations in the description.
7. `contentplus` (our) resolver: Trains `fasttext` models using supervised learning on a set of tweets by users from various locations. There's an option for users to resolve the tweets country-wise in states, or a global city-wise resolution. The first approach is more robust to errors than the second approach.

*Note: `bioplus` and `contentplus` resolutions are prone to errors, thus resolutions marked with red flag in the analysis output file are recommended to be cross-checked by the user. Users will need to download our pre-trained models from [here](), and store them in `models/` directory*  

## Tutorials

## Contributions

### How to contribute
### Goals 

## Citation

## Contact
Varad Pimpalkhute <pimpalkhutevarad@gmail.com>
