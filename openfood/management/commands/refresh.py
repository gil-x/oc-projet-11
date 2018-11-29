from django.core.management.base import BaseCommand, CommandError
from openfood.models import Product, Category, Position
from django.db import models
from datetime import datetime

import sys
import requests


class Collector:
    """
    Get products from Open Food Facts database.
    Register fields for 'Products' & 'Categories'.
    The many to many connection table 'Position' contains 'rank' field,
    according to the position of each category in the product hierarchy.
    """

    def __init__(self, url="https://fr.openfoodfacts.org/cgi/search.pl",
            number_by_grade=[
                ('a', 150), ('b', 150), ('c', 150), ('d', 150), ('e', 150)
                ],
                categories=[
                    "Salty snacks", "Cheeses", "Beverage", "Sauces",
                    "Biscuits", "Frozen foods", "pizzas", "chocolats",
                    "Candies", "Snacks sucrés",]
            ):
        self.url = url
        self.grades = number_by_grade
        self.categories = categories
        self.products = []

    def fetch(self, category="Cheese", grade="a", products_number=50,
            product_keys = [ 'product_name', 'nutrition_grades',
            'url', 'code', 'brands', 'stores', 'categories_hierarchy',
            'image_url', ]):
        """
        Get [products_number] products in  [category] & grade [grade,
        keep only the needed fields listed in [product_keys].
        """
        args = {
            'action': "process",
            'tagtype_0': "categories",
            'tag_contains_0': "contains",
            'tag_0': category,
            'nutrition_grades': grade,
            'json': 1,
            'page_size': 1000,
            }
        response = requests.get(self.url, params=args)
        products = response.json()["products"]
        products_to_store = []
        for product in products:
            product_to_store = {}
            try:
                for key in product_keys:
                    product_to_store[key] = product[key]
                products_to_store.append(product_to_store)
            except KeyError:
                # print("Key Error on {}.".format(key))
                pass

            if len(products_to_store) == products_number:
                print("Number reached !!!")
                break

        self.products.extend(products_to_store)


    def register(self):
        for product in self.products:
            new_product = Product()
            new_product.product_name = product['product_name']
            new_product.grade = product['nutrition_grades']
            new_product.url = product['url']
            new_product.barcode = product['code']
            new_product.brand = product['brands']
            new_product.store = product['stores']
            new_product.product_img_url = product['image_url']
            new_product.save()

            for i, category in enumerate(product['categories_hierarchy'][::-1]):
                new_category = Category.objects.get_or_create(
                    category_name=category,
                )
                new_position = Position()
                new_position.product = new_product
                new_position.category = new_category[0]
                new_position.rank = i
                new_position.save()

    def populate(self):
        for category in self.categories:
            for grade in self.grades:
                self.fetch(category=category, grade=grade[0],
                    products_number=grade[1])
                print("Products:", len(self.products))
        print("Registering products in database...")
        self.register()
        print("{} products registered in database.".format(len(self.products)))

    def empty(self):
        products_to_delete = Product.objects.filter(favorized=0)
        products_to_delete_number = len(products_to_delete)
        total_products = len(Product.objects.all())
        
        products_to_delete.delete()
        print("-\n{} deleted on a total of {}.-\n".format(
                products_to_delete_number,
                total_products,
                )
            )


        



class Command(BaseCommand):
    """
    Django command to refresh data.
    """
    def handle(self, *args, **options):
        collector = Collector()

        orig_stdout = sys.stdout

        if 'win' in sys.platform:
            filename = 'refresh_logs/refresh-{}.txt'.format(datetime.strftime(datetime.now(), "%d-%m-%Y@%H-%M-%S"))
        else:
            filename = '/home/gil/oc-projet-10/refresh_logs/refresh-{}.txt'.format(datetime.strftime(datetime.now(), "%d-%m-%Y@%H-%M-%S"))
        
        log = open(filename, 'w')
        sys.stdout = log

        print("Operation started at {}.\n-".format(datetime.strftime(datetime.now(), "%H:%M:%S")))

        collector.empty()
        collector.populate()

        print("-\nOperation ended at {}.".format(datetime.strftime(datetime.now(), "%H:%M:%S")))

        sys.stdout = orig_stdout