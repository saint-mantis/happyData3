from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.services import populate_happiness_data
import os


class Command(BaseCommand):
    help = 'Load World Happiness Report data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file-path',
            type=str,
            default='/Users/arunbabu/Desktop/Code/Happy Data 3/World_Happiness_Report_2020_2025.xlsx',
            help='Path to the Excel file with happiness data',
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Excel file not found: {file_path}')
            )
            return

        self.stdout.write(f'Loading happiness data from: {file_path}')
        self.stdout.write('This may take a few minutes...')
        
        try:
            with transaction.atomic():
                created, updated, unmapped = populate_happiness_data(file_path)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully loaded happiness data: {created} created, {updated} updated'
                    )
                )
                
                if unmapped:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Countries not mapped to World Bank codes ({len(unmapped)}): '
                            f'{", ".join(sorted(list(unmapped)[:10]))}{"..." if len(unmapped) > 10 else ""}'
                        )
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to load happiness data: {e}')
            )