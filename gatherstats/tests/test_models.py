import datetime

import django.db
from django.test import TestCase
from django.utils import timezone

from ..models import Statistic


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
