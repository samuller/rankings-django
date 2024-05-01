# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versions

There are a few different components in this project that each have their own versions:

- The main project version refers to the backend server and in this file we'll prefix its versions with `API`, e.g. `API 1.2.3`.
- The Single-Page App (SPA) web frontend has its own version which will be prefixed with `UI` in this file, e.g. `UI 1.2.3`.
- Various docker containers might also be built and they'll use one of the above versions. A backend-only or frontend-only container will use the corresponding version, while a full-stack container will use the frontend's version (as the frontend is then the final interface to the intended user).
  - Docker containers might also add an additional build number at the end of the version if they have multiple releases for the same version, e.g. `1.2.3-4`.

## [Unreleased]

> [!NOTE]
> We have summarised the project history below and added some revisionist versions, but proper (semantic) versioning was only started afterwards (above).

##  [3.0.0] - 2016-09-20 - 2022-03-01

###  Changed

- Start of this git repo.
- Started conversion of backend to use the [Django framework](https://www.djangoproject.com/) instead of Flask.
- Frontend kept same `Jinja` templates (instead of using `Django`'s templating language).
- Kept same data `SQLite` format and used `Django`'s [inspectdb](https://docs.djangoproject.com/en/1.10/howto/legacy-databases/) to auto-generate models.

## [2.0.0] - 2014-10-04 - 2016-05-21

###  Changed

- Converted backend to `Python` with the [Flask framework](https://flask.palletsprojects.com/) and two libraries: [Flask-WTF](https://flask-wtf.readthedocs.io/) (forms) and [Trueskill](https://trueskill.org/).
- Frontend stayed the same (except for conversion to `Jinja` templates).
- Also converted data format into `SQLite` database.
- Repo at [rankings-flask](https://github.com/samuller/rankings-flask).

## [1.0.0] - 2013-2014

### Added

- Site created with a `PHP` backend and the [PHPSkills](https://github.com/moserware/PHPSkills) library (inspired by this [blog post](https://www.moserware.com/2010/03/computing-your-skill.html)).
- The frontend was created with [Zurb Foundation 4](https://zurb.com/blog/foundation-4-is-here-the-smartest-foundat) and vanilla `JavaScript` with [HighCharts](https://www.highcharts.com/) charts.
- Data was stored in `CSV` files.
