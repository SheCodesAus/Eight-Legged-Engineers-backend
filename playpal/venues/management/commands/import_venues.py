import csv
from django.core.management.base import BaseCommand
from venues.models import Venue

class Command(BaseCommand):
    help = 'Import venues from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        created_count = 0
        skipped_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Helper to convert string to int or None
                    def to_int(value):
                        value = (value or '').strip()
                        return int(value) if value else None
                    
                    Venue.objects.create(
                        main_category=row['Main Category'],
                        sub_category=row['Sub Category'],
                        name=row.get('Name', '').strip(),
                        address=row['Address'],
                        suburb=row['Suburb'],
                        opening_times=row['Opening Times'],
                        min_age=to_int(row.get('Min Age')),
                        max_age=to_int(row.get('Max Age')),
                        cost=row['Cost'],
                        kids_eat_free=row['Kids Eat Free'],
                        indoor_outdoor=row['Indoor/Outdoor'],
                        wheelchair_friendly=row['Wheelchair Friendly'],
                        latitude=float(row['Latitude']),
                        longitude=float(row['Longitude']),
                        image_url=row['Image URL'],
                        is_published=(row['is_published'].strip().lower() == 'yes'),
                        is_archived=(row.get('is_archived', '').strip().lower() == 'yes'),
                        ratings_id=to_int(row.get('ratings_id')),
                    )
                    created_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f"Skipped row {row.get('ID', '?')}: {e}"
                    ))
                    skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Imported {created_count} venues, skipped {skipped_count}'
        ))