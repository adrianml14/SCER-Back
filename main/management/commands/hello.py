from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Display a simple greeting message'

    def handle(self, *args, **kwargs):
        #  add your custom logic here like fetching data from api when
        #  this command called
        #  for example
        self.stdout.write('Hello, World!')