from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.services import populate_countries, populate_indicators, populate_country_data


class Command(BaseCommand):
    help = 'Load World Bank countries, indicators, and data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--countries-only',
            action='store_true',
            help='Load only countries data',
        )
        parser.add_argument(
            '--indicators-only',
            action='store_true',
            help='Load only indicators data',
        )
        parser.add_argument(
            '--data-only',
            action='store_true',
            help='Load only country indicator data',
        )

    def handle(self, *args, **options):
        if options['countries_only']:
            self.load_countries()
        elif options['indicators_only']:
            self.load_indicators()
        elif options['data_only']:
            self.load_country_data()
        else:
            self.load_all()

    def load_countries(self):
        self.stdout.write('Loading countries from World Bank API...')
        try:
            with transaction.atomic():
                created, updated = populate_countries()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully loaded countries: {created} created, {updated} updated'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to load countries: {e}')
            )

    def load_indicators(self):
        self.stdout.write('Loading indicators from World Bank API...')
        try:
            with transaction.atomic():
                created, updated = populate_indicators()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully loaded indicators: {created} created, {updated} updated'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to load indicators: {e}')
            )

    def load_country_data(self):
        self.stdout.write('Loading country indicator data from World Bank API...')
        self.stdout.write('This may take several minutes...')
        try:
            with transaction.atomic():
                created, updated = populate_country_data()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully loaded country data: {created} created, {updated} updated'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to load country data: {e}')
            )

    def load_all(self):
        self.stdout.write('Loading all World Bank data...')
        
        # Load in order: countries -> indicators -> data
        self.load_countries()
        self.load_indicators()
        self.load_country_data()
        
        self.stdout.write(
            self.style.SUCCESS('All World Bank data loaded successfully!')
        )