# Netranker
[![Build Status](https://cloud.drone.io/api/badges/ouroboros8/netranker/status.svg?ref=refs/heads/master)](https://cloud.drone.io/ouroboros8/netranker)

This python app provides the APIs for netranker, a netrunner card crowd-ranking
website.

## Install

netranker is on pypi. To install, simply run

    pip install netranker

## Dependencies

Python dependencies are managed by
[pipenv](https://docs.pipenv.org/en/latest/). To install dependencies, run

    pipenv install

to install dev dependencies as well (required to run tests), use

    pipenv install -d

The default app config also expects a MongoDB server running on localhost:27017

## Run

To start the API server, run

    FLASK_APP=netranker/app.py pipenv run flask run
