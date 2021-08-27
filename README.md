# TwitterGeoLoc: An easy to use GeoTagging Tool

## Introduction
`TwitterGeoLoc` is a python library for resolving geo locations of users on Twitter. It makes use of various instances of data present in a given tweet and the corresponding user's profile. Some of the instances taken into consideration in the current version of `TwitterGeoLoc` are:
- *Tweet Meta Data*: Coordinates of user or Place Tag assigned to the tweet.
- *Location Tag*: Location provided by user in tag present on user's profile.
- *User's Bio*: Users can mention their living location in the description space available on their profile.
- *Tweet content*: Mentions of a location name in a tweet.
The above four instances are ordered in a decreasing order of importance with the Tweet Metdata having the most precise information to tweet content having the least precise information. 

`TweetGeoLoc` has been developed by keeping [carmen](https://github.com/mdredze/carmen-python/tree/v0.0.3) as a base and improving on the various drawbacks present in it. Some key features of `TweetGeoLoc` are:
1. Lightweight and fast.
2. Comes with an improved location database.
3. Options available for using user aggregation.
4. Uses population heuristics to resolve locations with conflicts.
5. Allows to classify locations in tweet content country wise.
6. Possible to train new model and improve location database.
7. Performance benchmarked with other popular tools.
There's a lot of room for improving `TweetGeoLoc`. Depending on how the system develops, we may consider seperating it from `carmen` and build our own API. We are happy to receive contributions. Please check the instructions in the **Contributions** Section for contributing.

## Quick Start


## Directory Structure
The directory structure after installation and downloading the models should be:
```ascii
TwitterGeoLoc/
├─ carmen/
│  ├─ data/
│  │  ├─ gpkg_radius_all.tsv
│  │  ├─ locations_error_resolved_v3.json
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

## Tutorials

## Contributions

### How to contribute
### Goals 

## Citation

## Contact
Varad Pimpalkhute <pimpalkhutevarad@gmail.com>
