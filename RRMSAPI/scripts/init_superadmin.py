# scripts/init_superadmin.py

import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Step 1: Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RRMSAPI.settings')  # Replace with your settings module
django.setup()

# Step 2: Import models after setup
from users.models import User, Role  # Replace 'yourapp' with actual app name

# Step 3: Create SuperAdmin role if not exists
role, created = Role.objects.get_or_create(roleId=1, defaults={"name": "SuperAdmin"})

# Step 4: Create the superuser if not exists
if not User.objects.filter(email="admin@gmail.com").exists():
    user = User(
        kgid="000000",
        email="admin@example.com",
        first_name="Super",
        last_name="Admin",
        role=role,
        is_staff=True,
        is_superuser=True,
        is_active=True,
        is_passwordset=True
    )
    user.set_password("Dgcid@123")  # ✅ Securely hash the password
    user.save()

    print("✅ SuperAdmin user created.")
else:
    print("⚠️ SuperAdmin user already exists.")
