"""
Management command to generate a permanent client ID for a user
Usage: python manage.py generate_client_id <username>
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.authentication.models import ClientSession
import secrets


class Command(BaseCommand):
    help = 'Generate a permanent client ID for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to generate client ID for')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            return
        
        # Generate client ID
        client_id = f"client_{secrets.token_urlsafe(24)}"
        
        session = ClientSession.objects.create(
            user=user,
            client_id=client_id
        )
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('CLIENT ID GENERATED SUCCESSFULLY'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'\nUser: {user.username}')
        self.stdout.write(f'\n{self.style.WARNING("Client ID:")} {self.style.SUCCESS(session.client_id)}')
        self.stdout.write(f'\nCreated: {session.created_at}')
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write('\nUSAGE:')
        self.stdout.write('Add this header to all API requests:')
        self.stdout.write(f'  {self.style.WARNING("X-Client-ID:")} {session.client_id}')
        self.stdout.write('\nExample with curl:')
        self.stdout.write(f'  curl -H "X-Client-ID: {session.client_id}" http://localhost:8000/api/customer/itr/')
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.WARNING('\n⚠ IMPORTANT: Save this client ID securely!\n'))


