import csv

from receipts.models import Ingredient


def run():
    data = '../data/ingredients.csv'
    with open(data, encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            ingredients = Ingredient(name=row[0], measurement_unit=row[1])
            ingredients.save()
