"""
gatherstats
-----------

Gather statistics from an IAR endpoint and write records to the DB.

"""
import json
from urllib.parse import urlsplit, urlunsplit

from django.core.management.base import BaseCommand
from django.utils import timezone
import requests

from gatherstats.models import Statistic


class Command(BaseCommand):
    """Implementation of gatherstats management command."""

    help = 'Gather IAR statistics from an API endpoint'

    def add_arguments(self, parser):
        parser.add_argument(
            'stats_endpoint', metavar='URL_OR_PATH', type=str,
            help='URL pointing to or file containing an IAR stats resource')
        parser.add_argument(
            '--endpoint', metavar='URL', type=str,
            help='Override the endpoint used to record this statistic in the database')

    def handle(self, *args, **options):
        # Take argument and parse as URL. If the scheme is empty, use file.
        endpoint_parts = urlsplit(options['stats_endpoint'], scheme='file')
        endpoint = urlunsplit(endpoint_parts)

        # Allow overriding the endpoint from CLI
        if options['endpoint'] is not None:
            endpoint = options['endpoint']

        # Fetch stats and record the time the fetch completed
        body = (
            _file_contents(endpoint_parts.path)
            if endpoint_parts.scheme == 'file' else
            _url_contents(endpoint)
        )
        fetched_at = timezone.now()

        # Create Statistics
        objects = Statistic.objects.create_from_stats_response(
            endpoint=endpoint, body=body, fetched_at=fetched_at
        )

        print('Created {} object(s)'.format(len(objects)), file=self.stdout)


def _url_contents(url):
    """GET a URL and parse body as JSON."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def _file_contents(path):
    """Return contents of file parsed as JSON."""
    with open(path) as fobj:
        return json.load(fobj)
