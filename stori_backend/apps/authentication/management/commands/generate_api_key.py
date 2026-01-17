"""
Management command to generate a permanent API key for a user
Usage: python manage.py generate_api_key <username> <key_name>
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.authentication.models import APIKey


class Command(BaseCommand):
    help = 'Generate a permanent API key for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to generate API key for')
        parser.add_argument('key_name', type=str, help='Name/description for the API key')

    def handle(self, *args, **options):
        username = options['username']
        key_name = options['key_name']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            self.stdout.write(self.style.WARNING('Creating default user "admin"...'))
            
            # Create a default admin user
            user = User.objects.create_user(
                username='admin',
                email='admin@stori.com',
                password='admin123',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created user: admin (password: admin123)'))
        
        # Generate API key
        api_key = APIKey.objects.create(
            user=user,
            name=key_name
        )
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('API KEY GENERATED SUCCESSFULLY'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'\nUser: {user.username}')
        self.stdout.write(f'Key Name: {api_key.name}')
        self.stdout.write(f'\n{self.style.WARNING("API Key:")} {self.style.SUCCESS(api_key.key)}')
        self.stdout.write(f'\nCreated: {api_key.created_at}')
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write('\nUSAGE:')
        self.stdout.write('Add this header to all API requests:')
        self.stdout.write(f'  {self.style.WARNING("X-API-Key:")} {api_key.key}')
        self.stdout.write('\nExample with curl:')
        self.stdout.write(f'  curl -H "X-API-Key: {api_key.key}" http://localhost:8000/api/customer/itr/')
        self.stdout.write('\nExample with Python requests:')
        self.stdout.write(f'  headers = {{"X-API-Key": "{api_key.key}"}}')
        self.stdout.write('  requests.get("http://localhost:8000/api/customer/itr/", headers=headers)')
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.WARNING('\n⚠ IMPORTANT: Save this API key securely!'))
        self.stdout.write('It will not be shown again.\n')


