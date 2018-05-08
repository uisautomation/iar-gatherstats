from django.db import models, transaction
from django.utils import timezone


def _flatten_dict(d, prefix_path=[]):
    """A generator which yields key/value pairs from a flattened dict. E.g., given the following
    dict::

        {
            'foo': 45,
            'bar': {
                'buzz': 70,
                'bang': 'hello',
            },
            'quux': {},  # empty dicts are ignored
        }

    This function generates the following pairs::

        ('foo', 45)
        ('bar.buzz', 70)
        ('bar.bang', 'hello')

    The ordering is not guaranteed beyond the dictionary will be explored in a breadth first
    manner.

    """
    if not isinstance(d, dict):
        raise TypeError('_flatten_dict() must be passed a dict')

    dict_items = []
    for k, v in d.items():
        if not isinstance(v, dict):
            yield '.'.join(prefix_path + [k]), v
        else:
            dict_items.append((k, v))

    # Process dict items after all non-dict items to ensure breadth-first navigation
    for k, v in dict_items:
        assert isinstance(v, dict)
        for item in _flatten_dict(v, prefix_path=prefix_path + [k]):
            yield item


class StatisticManager(models.Manager):
    """
    Custom object manager for :py:class:`Statistic`. Accessed via :py:attr:`Statistic.objects`.
    """

    @transaction.atomic
    def create_from_stats_response(self, endpoint, body, fetched_at=None):
        """Create :py:class:`Statistic` instances from a dictionary representation of a stats
        endpoint response body.

        The object creation is done within a database atomic transaction so other users of the
        database never see a partially processed object.

        If *fetched_at* is None, :py:func:`timezone.now` is used.

        """
        fetched_at = fetched_at if fetched_at is not None else timezone.now()

        created_objects = [
            Statistic.objects.create(
                endpoint=endpoint, key=key, numeric_value=value, fetched_at=fetched_at
            )
            for key, value in _flatten_dict(body)
        ]

        return created_objects


class Statistic(models.Model):
    """
    Statistics from the IAR stats endpoint look like the following:

    .. code:: js

        {
            "asset_counts": {
                "all": {
                    "total": 1234,
                    "completed": 1234,
                    "with_personal_data": 1234
                },
                "by_institution": {
                    "INSTA": {
                        "total": 123,
                        "completed": 123,
                        "with_personal_data": 123
                    }
                    // ... etc
                }
            }
        }

    In order to allow this schema to change in the future, we convert this structured table into a
    series of rows recording the JavaScript-style key path and the value. For example, one row from
    the above would be created as::

        from django.utils import timezone
        from gatherstats.models import Stat

        Statistic(
            endpoint='http://iar-backend.invalid/stats',
            key='asset_counts.by_institution.INSTA.completed',
            numeric_value=123,
            fetched_at=now(),
        )

    Sufficiently clever SQL can be used to query various things from this DB. For example, to get a
    list of all institutions with available statistics:

    .. code:: sql

        SELECT DISTINCT
            SUBSTRING(key FROM '^by_institution\.([^\.]+)\.[^\.]+$') AS institution
        FROM
            gatherstats_statistic
        WHERE key ~ '^by_institution\.([^\.]+)\.[^\.]+$'
        ORDER BY
            institution;

    """
    objects = StatisticManager()

    #: URL for the endpoint this statistic was fetched from.
    endpoint = models.URLField(
        max_length=1204,
        help_text='URL of endpoint which this stat was fetched from')

    #: Key path for statistic. E.g. "asset_counts.by_institution.UIS.total".
    key = models.CharField(
        max_length=512,
        help_text='Dot-separated JavaScript style key path')

    #: This field is called "numeric_value" to allow for other types to be stored in the future.
    #: When that future comes, this field needs to have null and blank set to True and a custom
    #: validation will need to be added that checks that *some* value is set. In these simpler
    #: times, we can just rely on this being a non-NULL, non-blank field.
    numeric_value = models.FloatField(
        help_text='Value of numeric statistic')

    #: By design, this schema "flattens" statistics into rows and multiple rows may represent a
    #: single query to the stats endpoint. It is for this reason that we do not default this to
    #: now() and instead require that it be set explicitly.
    fetched_at = models.DateTimeField(
        help_text='Date and time when this statistic was fetched')

    class Meta:
        unique_together = (
            # A given endpoint must only have one key value for a given fetched at time.
            ('endpoint', 'key', 'fetched_at'),
        )

        indexes = [
            # Generate indices for endpoints and fetched at value alone and the
            # endpoint/key/fetched_at combination since these are likely to be the most common
            # filtering options. More indexes can be created should it become necessary.
            models.Index(fields=['endpoint']),
            models.Index(fields=['endpoint', 'key', 'fetched_at']),
        ]
