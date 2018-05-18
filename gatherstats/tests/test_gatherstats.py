"""
Test the gatherstats management command.

"""
import contextlib
import io
import json
import os
import tempfile
import unittest.mock as mock

from django.core.management import call_command
from django.test import TestCase

from gatherstats.models import Statistic, _flatten_dict


STATS_FIXTURE = json.dumps({
    'asset_counts': {
        'all': {'total': 100, 'completed': 87},
        'by_institution': {
            'INSTA': {'total': 50, 'completed': 5},
            'INSTB': {'total': 20, 'completed': 15},
        },
    }
})

STATS_ITEMS = list(_flatten_dict(json.loads(STATS_FIXTURE)))


@contextlib.contextmanager
def temporary_file_with_contents(contents):
    """Within the context, a temporary file is created with the contents set to the passed string.
    The context returns the temporary file's name from __enter__().

    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        filename = os.path.join(tmp_dir, 'temp')
        with open(filename, 'w') as fobj:
            fobj.write(contents)
        yield filename


class GatherstatsTest(TestCase):
    def test_file_load(self):
        out = io.StringIO()
        with temporary_file_with_contents(STATS_FIXTURE) as filename:
            expected_endpoint = 'file://' + filename
            call_command('gatherstats', filename, stdout=out)

        # Output included the expected number of objects
        self.assertIn(' {} '.format(len(STATS_ITEMS)), out.getvalue())

        self.assertEqual(Statistic.objects.all().count(), len(STATS_ITEMS))

        for key, value in STATS_ITEMS:
            self.assertTrue(Statistic.objects.filter(
                endpoint=expected_endpoint, key=key, numeric_value=value).exists())

    def test_url_load(self):
        out = io.StringIO()
        url = 'http://iar-backend.invalid/stats'
        with mock.patch('requests.get') as get:
            get.return_value.json.return_value = json.loads(STATS_FIXTURE)
            call_command('gatherstats', url, stdout=out)

        get.assert_called_with(url)

        # Output included the expected number of objects
        self.assertIn(' {} '.format(len(STATS_ITEMS)), out.getvalue())

        self.assertEqual(Statistic.objects.all().count(), len(STATS_ITEMS))

        for key, value in STATS_ITEMS:
            self.assertTrue(Statistic.objects.filter(
                endpoint=url, key=key, numeric_value=value).exists())

    def test_file_load_with_custom_endpoint(self):
        endpoint = 'http://custom.invalid/api'
        out = io.StringIO()
        with temporary_file_with_contents(STATS_FIXTURE) as filename:
            call_command('gatherstats', filename, stdout=out, endpoint=endpoint)

        # Output included the expected number of objects
        self.assertIn(' {} '.format(len(STATS_ITEMS)), out.getvalue())

        self.assertEqual(Statistic.objects.all().count(), len(STATS_ITEMS))

        for key, value in STATS_ITEMS:
            self.assertTrue(Statistic.objects.filter(
                endpoint=endpoint, key=key, numeric_value=value).exists())
