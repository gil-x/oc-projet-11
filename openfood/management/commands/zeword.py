from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    This is a fake command to test... the testing!
    """
    def handle(self, *args, **options):
        zeword = "Lion"
        print("zeword:", zeword)