"""
Test the gatherstats management command.

"""

from io import StringIO
from django.core.management import call_command
from django.test import TestCase


class GatherstatsTest(TestCase):
    def test_basic_functionality(self):
        out = StringIO()
        call_command('gatherstats', stdout=out)
        self.assertIn('Hello, world', out.getvalue())
