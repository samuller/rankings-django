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

## [Docker 4.0.1-1.0.1] - 2024-05-09

### Changed

- Docker: versioning of combined container now includes both API & UI versions.
- API: enable logging of API errors to console when Django's debug mode is disabled.

### Fixed

- UI: fix table having wrong colors when browser uses light mode theme (looking like white box).
- Docker: start-up errors of API will no longer flood logs as `autorestart` is disabled in `supervisord` service.

### Added

- API: start-up check added to see and error if database file isn't writable.
- Deploy: scripts added to help with deployments: `rankings-docker.service` & `ubuntu-motd`.
- Docker: combined container now supports "static sites" that are served by Caddy if the correct folder & configs are mounted (see [README](deploy/static-sites/README.md)).

## [Docker 1.0.0] - 2024-05-01

- Versions: `API 4.0.0` & `UI 1.0.0`

### Added

- Started experimenting with `Svelte` in first half of 2023 and looking for a UI/component framework:
  - 2023-08-17: Started experimenting with [DaisyUI](https://daisyui.com/) component library.
  - 2023-08-27: Updated `Django` to 3.2 and added [Django REST Framework](https://www.django-rest-framework.org/) (DRF) extension in preparation for a REST API that can be used by a Single-Page App (SPA) website.
  - 2023-09-02: Merged "svelte-ui" branch into "master". Makes use of [SvelteKit](https://kit.svelte.dev/) framework.
- 2023-09-16: Started creating Docker image.
  - 2023-10-02: Uploaded first docker image (v0.9.0) to Docker Hub at `samuller/rankings-site-test`.
  - 2024-05-01: Uploaded `samuller/rankings-site` docker image (v1.0.0) with these versions: API `4.0.0` / UI `1.0.0`.

---

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
