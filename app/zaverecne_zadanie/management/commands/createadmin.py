import getpass

from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.exceptions import ValidationError
from zaverecne_zadanie.models import User


class Command(BaseCommand):
    help = 'Creates a superuser with custom required fields.'

    def handle(self, *args, **options):
        email = input("Email: ")
        ais_id = input("AIS ID: ")
        first_name = input("First name: ")
        last_name = input("Last name: ")
        password = getpass.getpass("Password: ")
        password2 = getpass.getpass("Password (again): ")

        if password != password2:
            self.stderr.write("Error: Passwords don't match.")
            return

        try:
            User.objects.create_superuser(email=email, ais_id=ais_id, first_name=first_name, last_name=last_name,
                                          password=password, username=f'x{last_name}')
            self.stdout.write("Superuser created successfully.")
        except ValidationError as e:
            self.stderr.write("Error: {}".format(e.message_dict))
