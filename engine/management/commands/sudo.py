import os
from django.core.management.base import BaseCommand

from core.models.users import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(email= os.environ.get('SUDO_EMAIL')).exists():
            User.objects.create_superuser(email=os.environ.get('SUDO_EMAIL'), username='', password=os.environ.get('SUDO_PASS'))