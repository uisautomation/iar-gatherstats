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

## Running a stats gather job

A one-off gather job can be triggered by directly running the Docker image and
specifying the database location and credentials via environment variables.

```bash
# Replace DJANGO_DB_... environment variable values as appropriate
$ docker run uisautomation/iar-gatherstats gatherstats                        \
	-e DJANGO_DB_ENGINE=django.db.backends.postgresql                     \
	-e DJANGO_DB_HOST=postgres.invalid -e DJANGO_DB_NAME=statsdb          \
	-e DJANGO_DB_USER=statsdb-user -e DJANGO_DB_PASSWORD=statsdb-password \
	https://iar-backend.gcloud.automation.uis.cam.ac.uk/stats
```

The Google Cloud SQL proxy can be used to expose a Google Cloud hosted database
as a locally hosted service.

## Developer quickstart

Once this repository is cloned, a developer can quickly run a gatherstats job
using the [manage_development.sh](manage_development.sh) script:

```bash
# Perform an initial database migration
$ ./manage_development.sh migrate

# Gather stats from the endpoint
$ ./manage_development.sh gatherstats https://iar-backend.gcloud.automation.uis.cam.ac.uk/stats

# Open a database shell
$ ./manage_development.sh dbshell
```

One can then query the database directly. For example, to see the "all entries"
summaries ordered by fetch time:

```sql
SELECT
  *
FROM
  gatherstats_statistic
WHERE
  key LIKE 'all.%'
ORDER BY
  fetched_at DESC;
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
