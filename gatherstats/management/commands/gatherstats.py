"""
gatherstats
-----------

Gather statistics from an IAR endpoint and write records to the DB.

"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Implementation of gatherstats management command."""

    help = 'Gather IAR statistics from an API endpoint'

    def handle(self, *args, **options):
        print('Hello, world', file=self.stdout)
