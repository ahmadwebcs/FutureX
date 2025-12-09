import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create a superuser with credentials from environment or defaults'

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        name = os.getenv('DJANGO_SUPERUSER_NAME', 'Admin')
        cnic = os.getenv('DJANGO_SUPERUSER_CNIC', '00000-0000000-0')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'adminpass')

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superuser with email {email} already exists'))
            return

        user = User.objects.create_superuser(email=email, name=name, cnic=cnic, password=password)
        self.stdout.write(self.style.SUCCESS(f'Created superuser {email}'))
        self.stdout.write(f'EMAIL={email}\nPASSWORD={password}')
