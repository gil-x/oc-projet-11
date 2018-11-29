from django.core.management.base import BaseCommand, CommandError
from openfood.models import Product, Category, Position
from django.db import models
from datetime import datetime

import sys
import requests


class HelloMachine:
    """
    Hello world.
    """

    def __init__(self):
        pass

    def say_hello(self):
        print("Hello world!")



class Command(BaseCommand):
    """
    Create a sample text file.
    """
    def handle(self, *args, **options):
        hello_machine = HelloMachine()

        orig_stdout = sys.stdout

        if 'win' in sys.platform:
            filename = 'refresh_logs/hello-{}.txt'.format(datetime.strftime(datetime.now(), "%d-%m-%Y@%H-%M-%S"))
        else:
            filename = '/home/gil/oc-projet-10/refresh_logs/hello-{}.txt'.format(datetime.strftime(datetime.now(), "%d-%m-%Y@%H-%M-%S"))

        log = open(filename, 'w')
        sys.stdout = log

        print("Operation started at {}.\n-".format(datetime.strftime(datetime.now(), "%H:%M:%S")))

        hello_machine.say_hello()

        print("-\nOperation ended at {}.".format(datetime.strftime(datetime.now(), "%H:%M:%S")))

        sys.stdout = orig_stdout