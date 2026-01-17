"""
Quick script to check API keys in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import APIKey

print("=" * 70)
print("ACTIVE API KEYS IN DATABASE")
print("=" * 70)

keys = APIKey.objects.all().select_related('user')

if not keys:
    print("\n[ERROR] No API keys found in database!")
    print("\nTo create one, run:")
    print("  python manage.py generate_api_key admin 'Production API Key'")
else:
    for key in keys:
        status = "[ACTIVE]" if key.is_active else "[INACTIVE]"
        print(f"\n{status}")
        print(f"  Name: {key.name}")
        print(f"  Key: {key.key}")
        print(f"  User: {key.user.username}")
        print(f"  Created: {key.created_at}")
        if key.last_used_at:
            print(f"  Last Used: {key.last_used_at}")
        else:
            print(f"  Last Used: Never")

print("\n" + "=" * 70)
print("TESTING API KEY")
print("=" * 70)

test_key = "stori_6CFocXsPyo4tJDxq8MkVE6Iy-aii0_7eN59VJvUlfmU"
try:
    api_key = APIKey.objects.get(key=test_key)
    if api_key.is_active:
        print(f"\n[SUCCESS] Key found and ACTIVE!")
        print(f"   User: {api_key.user.username}")
        print(f"   Name: {api_key.name}")
    else:
        print(f"\n[WARNING] Key found but INACTIVE!")
        print(f"   Please activate it in admin panel")
except APIKey.DoesNotExist:
    print(f"\n[ERROR] Key NOT FOUND in database!")
    print(f"   The key '{test_key}' does not exist.")
    print(f"\n   To create it, run:")
    print(f"   python manage.py generate_api_key admin 'Production API Key'")

print("\n" + "=" * 70)

