import csv

from app.models import Ingredient

from django.core.management import BaseCommand

from foodgram_backend.settings import LOAD_DATA_DIR


class Command(BaseCommand):
    """Command to upload ingredients to the database from a csv file."""

    def handle(self, *args, **options):
        with open(
                f'{LOAD_DATA_DIR}/ingredients.csv',
                encoding='utf-8',
        ) as csvfile:
            reader = csv.reader(csvfile)
            temp_data = [Ingredient(
                name=row[0],
                measurement_unit=row[1],
            ) for row in reader]
            Ingredient.objects.bulk_create(temp_data)
            self.stdout.write(self.style.SUCCESS(
                'Ingredients have been uploaded to the database')
            )
