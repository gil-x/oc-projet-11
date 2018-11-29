from django.core.management.base import BaseCommand, CommandError
from openfood.models import Product, Category, Position
from django.db import models
from datetime import datetime

import sys
import requests


class Counter:
    """
    Just count products and write it on a log file.
    """
    def __init__(self, logfile):
        self.logfile = logfile

    def count(self):
        total = len(Product.objects.all())
        favorites = len(Product.objects.exclude(favorized=0))
        no_favorites = len(Product.objects.filter(favorized=0))

        self.write_to_log("There are {} products registered in database:".format(total))
        self.write_to_log("\t- {} of them are registered as favorites.".format(favorites))
        self.write_to_log("\t- {} are not registered as favorites.".format(no_favorites))

    def write_to_log(self, text):
        log = open(self.logfile, 'a')
        log.write(text + "\n")
        log.close()


class Command(BaseCommand):
    """
    Django command to count products.
    """
    def handle(self, *args, **options):
        if 'win' in sys.platform:
            logfile = 'refresh_logs/product-count-{}.txt'.format(datetime.strftime(datetime.now(), "%d-%m-%Y@%H-%M-%S"))
        else:
            logfile = '/home/gil/oc-projet-10/refresh_logs/product-count-{}.txt'.format(datetime.strftime(datetime.now(), "%d-%m-%Y@%H-%M-%S"))
        
        counter = Counter(logfile)

        counter.write_to_log("Operation started at {}.\n*****".format(datetime.strftime(datetime.now(), "%H:%M:%S")))
        counter.count()
        counter.write_to_log("*****\nOperation ended at {}.".format(datetime.strftime(datetime.now(), "%H:%M:%S")))

