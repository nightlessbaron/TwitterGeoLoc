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
│  ├─ data/
│  ├─ evaluation/
│  ├─ test_labels/
├─ error-analysis/
│  ├─ analysis.csv
│  ├─ output.json
├─ metadata/
│  ├─ screen_name.json
│  ├─ ...
├─ .gitattributes
├─ README.md
└─ setup.py
```

## Usage

## Tutorials

## Contributions

### How to contribute
### Goals 

## Citation

## Contact
Varad Pimpalkhute <pimpalkhutevarad@gmail.com>