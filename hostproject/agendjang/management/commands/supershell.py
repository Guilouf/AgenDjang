from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    python3.6 manage.py supershell
    """
    help = 'Execute in Django context stuff you want'

    @staticmethod
    def do_stuff():
        pass

    def handle(self, *args, **options):
        self.do_stuff()
