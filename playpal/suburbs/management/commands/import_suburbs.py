import csv
from django.core.management.base import BaseCommand
from suburbs.models import Suburb

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        with open(options['file_path'], newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Suburb.objects.get_or_create(
                    suburb=row['suburb'].strip(),
                    state=row['state'].strip().upper(),
                    postcode=row['postcode'].strip(),
                )
        self.stdout.write(self.style.SUCCESS('Done'))