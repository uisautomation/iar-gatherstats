import datetime
import unittest.mock as mock

import django.db
from django.test import TestCase
from django.utils import timezone

from ..models import Statistic, _flatten_dict


class StatisticUniquenessTests(TestCase):
    def setUp(self):
        self.endpoint = 'https://iar-backend.invalid/'
        self.key = 'some.statistics.key'
        self.then = timezone.make_aware(datetime.datetime(
            year=2013, month=12, day=11, hour=10, minute=9, second=8
        ))

    def test_uniqueness(self):
        """An endpoint, key, fetched_at tuple must be unique."""
        Statistic.objects.create(
            endpoint=self.endpoint, key=self.key, fetched_at=self.then,
            numeric_value=123
        )

        with self.assertRaises(django.db.IntegrityError):
            Statistic.objects.create(
                endpoint=self.endpoint, key=self.key, fetched_at=self.then,
                numeric_value=456
            )


class StatisticCreateTests(TestCase):
    def setUp(self):
        self.endpoint = 'https://iar-backend.invalid/'
        self.response_body = {
            'asset_counts': {
                'all': {'total': 1234, 'complete': 7},
                'by_institution': {
                    'INSTA': {'total': 7, 'complete': 4},
                    'INSTB': {'total': 103, 'complete': 7},
                }
            },
        }
        self.then = timezone.make_aware(datetime.datetime(
            year=2013, month=12, day=11, hour=10, minute=9, second=8
        ))

    def test_create_from_response(self):
        """Creating objects from a response succeeds."""
        objects = Statistic.objects.create_from_stats_response(
            endpoint=self.endpoint, body=self.response_body, fetched_at=self.then
        )

        # The right number were created
        self.assertEqual(len(objects), 6)

        # The objects exist in the database
        for o in objects:
            self.assertIsNotNone(o.pk)

        # Test an object was created
        qs = Statistic.objects.filter(key='asset_counts.by_institution.INSTA.total')
        self.assertEqual(qs.count(), 1)
        o = qs.first()
        self.assertEqual(o.endpoint, self.endpoint)
        self.assertEqual(o.fetched_at, self.then)
        self.assertEqual(o.numeric_value, 7)

    def test_create_from_response_with_default_fetched_at(self):
        """Creating objects from a response succeeds with default fetched at."""
        with mock.patch('django.utils.timezone.now') as now:
            now.return_value = self.then
            Statistic.objects.create_from_stats_response(
                endpoint=self.endpoint, body=self.response_body
            )

        now.assert_called_with()

        # Test an object was created with the right fetched_at
        qs = Statistic.objects.filter(key='asset_counts.by_institution.INSTB.total')
        self.assertEqual(qs.count(), 1)
        o = qs.first()
        self.assertEqual(o.endpoint, self.endpoint)
        self.assertEqual(o.fetched_at, self.then)
        self.assertEqual(o.numeric_value, 103)

    def test_atomicity(self):
        """Objects are not created if there is a failure."""
        self.response_body['some'] = {
            'deep': {
                'foo': 13,

                # have the error deep down so that we do not encounter it first
                'dict': {'key': None}
            }
        }

        # Creation should fail
        with self.assertRaises(django.db.IntegrityError):
            Statistic.objects.create_from_stats_response(
                endpoint=self.endpoint, body=self.response_body
            )

        # There should be no objects in the dB
        self.assertEqual(Statistic.objects.all().count(), 0)


class FlattenDictTests(TestCase):
    def test_flatten_dict(self):
        items = set(_flatten_dict({
            'foo': 45,
            'bar': {
                'buzz': 70,
                'bang': 'hello',
            },
            'quux': {},
        }))

        self.assertEqual(len(items), 3)
        self.assertIn(('foo', 45), items)
        self.assertIn(('bar.buzz', 70), items)
        self.assertIn(('bar.bang', 'hello'), items)

    def test_type_error(self):
        """Passing a non-dict raises a type error on first iteration."""
        with self.assertRaises(TypeError):
            # NB: until the generator is iterated, the exception is not raised
            list(_flatten_dict([]))
