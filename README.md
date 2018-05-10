# Gather statistics for the IAR

[![Build
Status](https://travis-ci.org/uisautomation/iar-gatherstats.svg?branch=master)](https://travis-ci.org/uisautomation/iar-gatherstats)
![Docker Automated
build](https://img.shields.io/docker/automated/uisautomation/iar-gatherstats.svg)

This project provides a Django application intended to gather statistics from
the [IAR backend server](https://github.com/uisautomation/iar-backend).

## Documentation

The [documentation](https://uisautomation.github.io/iar-gatherstats) is hosted
via GitHub pages.

## Quickstart

```bash
# Replace DJANGO_DB_... environment variable values as appropriate
$ docker run uisautomation/iar-gatherstats gatherstats                        \
	-e DJANGO_DB_ENGINE=django.db.backends.postgresql                     \
	-e DJANGO_DB_HOST=postgres.invalid -e DJANGO_DB_NAME=statsdb          \
	-e DJANGO_DB_USER=statsdb-user -e DJANGO_DB_PASSWORD=statsdb-password \
	https://iar-backend.gcloud.automation.uis.cam.ac.uk/stats
```

## Docker image

The
[uisautomation/iar-gatherstats](https://hub.docker.com/r/uisautomation/iar-gatherstats/)
image is available from Docker hub. The default entry point is the Django
``manage.py`` script.

### Configuration

The following environment variables configure the Docker image:

* ``DJANGO_SETTINGS_MODULE``: The image will use
    [gatherstats_project.settings.docker](gatherstats_project/settings/docker.py)
    by default unless this environment variable is set.
* ``DJANGO_DB_ENGINE``: Django database engine. Default: use SQLite.
* ``DJANGO_DB_HOST``: Database server hostname. Default: ``None``.
* ``DJANGO_DB_PORT``: Database server port. Default: ``None``.
* ``DJANGO_DB_NAME``: Database name. Default: ``None``.
* ``DJANGO_DB_USER``: Username used to connect to database. Default: ``None``.
* ``DJANGO_DB_PASSWORD``: Password used to connect to database. Default:
    ``None``.

### Secret key

The Docker image bakes in a "secret" key to the image because it is currently
unused by any of the features. If this worries you, set the
``DJANGO_SECRET_KEY`` environment variable when running the container.
