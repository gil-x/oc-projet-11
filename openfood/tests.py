import requests
from requests.models import Response
from django.test import TestCase, Client
from unittest.mock import Mock, patch, MagicMock
from django.core.management import call_command
from .management.commands.initialize import Collector
from .models import Product, Category, Position


class CommandsTestCase(TestCase):
    def test_zeword(self):
        " Test my fake custom command."
        call_command('zeword')

    def test_initialize(self):
        response = Response()
        response.status_code = 200
        response.json = MagicMock(return_value={
            'products': [
            {
                'product_name': 'ProductA',
                'nutrition_grades': 'a',
                'url': 'http://off/product-a',
                'code': 100000000000,
                'brands': 'The A products',
                'stores': 'A store',
                'image_url': 'http://off/product-a/product_a.jpg',
                'categories_hierarchy': ['CatC', 'CatH', 'CatS', 'CatZ'],
            },
            {
                'product_name': 'ProductB',
                'nutrition_grades': 'b',
                'url': 'http://off/product-b',
                'code': 200000000000,
                'brands': 'The B products',
                'stores': 'B store',
                'image_url': 'http://off/product-b/product_b.jpg',
                'categories_hierarchy': ['CatC', 'CatH', 'CatS', 'CatZ'],
            },
            {
                'product_name': 'ProductC',
                'nutrition_grades': 'c',
                'url': 'http://off/product-c',
                'code': 300000000000,
                'brands': 'The C products',
                'stores': 'C store',
                'image_url': 'http://off/product-c/product_c.jpg',
                'categories_hierarchy': ['CatC', 'CatH', 'CatR', 'CatY'],
            },
            {
                'product_name': 'ProductD',
                'nutrition_grades': 'd',
                'url': 'http://off/product-d',
                'code': 400000000000,
                'brands': 'The D products',
                'stores': 'D store',
                'image_url': 'http://off/product-d/product_d.jpg',
                'categories_hierarchy': ['CatB', 'CatI', 'CatT', 'CatY'],
            },
            {
                'product_name': 'ProductE',
                'nutrition_grades': 'e',
                'url': 'http://off/product-e',
                'code': 500000000000,
                'brands': 'The E products',
                'stores': 'E store',
                'image_url': 'http://off/product-d/product_e.jpg',
                'categories_hierarchy': ['CatC', 'CatH', 'CatS', 'CatZ'],
            }
            ]
        })
        mocked_get = MagicMock(return_value=response)
        with patch('requests.get', mocked_get):
            collector = Collector(
                url="https://fr.openfoodfacts.org/cgi/search.pl",
                number_by_grade=[
                    ('a', 1), ('b', 1), ('c', 1), ('d', 1), ('e', 1)
                ],
                categories=['CatB', 'CatC', 'CatH', 'CatI', 'CatS', 'CatZ'],
                )
            collector.populate()


class ProductsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Create some products:
        ProductA with CatZ, CatS, CatH, CatC
        ProductB with CatZ, CatS, CatH, CatC
        ProductC with CatX, CatR, CatH, CatC
        ProductD with CatY, CatT, CatI, CatB
        ProductE with CatZ, CatS, CatH, CatC
        """
        products = [
            {
                'product_name': 'ProductA',
                'nutrition_grades': 'a',
                'url': 'http://off/product-a',
                'code': 100000000000,
                'brands': 'The A products',
                'stores': 'A store',
                'image_url': 'http://off/product-a/product_a.jpg',
                'categories_hierarchy': ['CatC', 'CatH', 'CatS', 'CatZ'],
            },
            {
                'product_name': 'ProductB',
                'nutrition_grades': 'b',
                'url': 'http://off/product-b',
                'code': 200000000000,
                'brands': 'The B products',
                'stores': 'B store',
                'image_url': 'http://off/product-b/product_b.jpg',
                'categories_hierarchy': ['CatC', 'CatH', 'CatS', 'CatZ'],
            },
            {
                'product_name': 'ProductC',
                'nutrition_grades': 'c',
                'url': 'http://off/product-c',
                'code': 300000000000,
                'brands': 'The C products',
                'stores': 'C store',
                'image_url': 'http://off/product-c/product_c.jpg',
                'categories_hierarchy': ['CatC', 'CatH', 'CatR', 'CatY'],
            },
            {
                'product_name': 'ProductD',
                'nutrition_grades': 'd',
                'url': 'http://off/product-d',
                'code': 400000000000,
                'brands': 'The D products',
                'stores': 'D store',
                'image_url': 'http://off/product-d/product_d.jpg',
                'categories_hierarchy': ['CatB', 'CatI', 'CatT', 'CatY'],
            },
            {
                'product_name': 'ProductE',
                'nutrition_grades': 'e',
                'url': 'http://off/product-e',
                'code': 500000000000,
                'brands': 'The E products',
                'stores': 'E store',
                'image_url': 'http://off/product-d/product_e.jpg',
                'categories_hierarchy': ['CatC', 'CatH', 'CatS', 'CatZ'],
            }
        ]
        for product in products:
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

    def test_search_product_page(self):
        """
        Test the Index page code response.
        """
        c = Client()
        response = c.get('/produits/recherche/')
        self.assertEqual(response.status_code, 200)

    def test_ramdom_product_page(self):
        """
        Test display of a ramdom chosen product.
        """
        c = Client()
        response = c.get('/produits/un-produit-au-hasard/')
        print("response.status_code:", response.status_code)
        self.assertEqual(response.status_code, 200)

    def test_existing_product_substitutes_page(self):
        """
        Test display of an existing product, id = 1.
        """
        c = Client()
        response = c.get('/produits/1/substituts/')
        self.assertEqual(response.status_code, 200)

    def test_no_existing_product_substitutes_page(self):
        """
        Test display of a non existing product, id = 100.
        """
        c = Client()
        response = c.get('/produits/100/substituts/')
        self.assertEqual(response.status_code, 404)

    def test_product_detail(self):
        """
        Test display of an existing product, id = 1.
        """
        c = Client()
        response = c.get('/produits/1/')
        self.assertEqual(response.status_code, 200)
