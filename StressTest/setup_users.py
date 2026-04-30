import time

import requests
import random

BASE_URL = "http://localhost"
ADMIN_EMAIL = "EnterEmail" # email админа
ADMIN_PASSWORD = "EnterPassword" # пароль админа

# Получаем токен админа
print("Getting admin token...")
response = requests.post(
    f"{BASE_URL}/v1/users/login",
    data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
)

if response.status_code != 200:
    print(f"Admin login failed: {response.status_code}")
    print(response.text)
    exit(1)

admin_token = response.json()["access_token"]
print(f"Admin token obtained")

# Создаём роль moderator, если её нет
print("Creating moderator role...")
response = requests.post(
    f"{BASE_URL}/v1/roles/create",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={"name": "moderator", "description": "Moderator role"}
)
if response.status_code == 200:
    print("Moderator role created")
elif response.status_code == 400 and "already exists" in response.text:
    print("Moderator role already exists")
else:
    print(f"Role creation response: {response.status_code}")

# Создаём 10 тестовых пользователей
created_users = []

for i in range(10):
    email = f"test_user_{i}@test.com"
    password = "Test123!"
    
    print(f"\nCreating user {i}: {email}")
    
    # Регистрация
    response = requests.post(
        f"{BASE_URL}/v1/users/register",
        json={
            "email": email,
            "password": password,
            "password_confirm": password
        }
    )
    
    if response.status_code == 200:
        print(f"  Created: {email}")
        created_users.append({"email": email, "password": password})
    elif response.status_code == 400 and "already exists" in response.text:
        print(f"  User already exists: {email}")
        created_users.append({"email": email, "password": password})
    else:
        print(f"  Failed: {response.status_code} - {response.text}")

# Ждём, чтобы данные записались в БД
time.sleep(1)

# Получаем всех пользователей (с пагинацией)
print("\nGetting all users...")
all_users = []
offset = 0
limit = 50

while True:
    response = requests.get(
        f"{BASE_URL}/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"offset": offset, "limit": limit}
    )
    
    if response.status_code != 200:
        print(f"Failed to get users: {response.status_code}")
        break
    
    users = response.json().get("users", [])
    if not users:
        break
    
    all_users.extend(users)
    offset += limit
    print(f"  Fetched {len(users)} users (total: {len(all_users)})")

# Назначаем роли
print("\nAssigning roles...")
for i, user_data in enumerate(created_users):
    email = user_data["email"]
    
    # Находим пользователя в списке
    user = next((u for u in all_users if u["email"] == email), None)
    
    if not user:
        print(f"  User not found: {email}")
        continue
    
    user_oid = user["oid"]
    print(f"  User {email}: oid={user_oid}")
    
    # Назначаем роль moderator каждому 3-му пользователю
    if i % 3 == 0:
        print(f"  Assigning moderator role to {email}")
        response = requests.post(
            f"{BASE_URL}/v1/users/oid_{user_oid}/roles/name_moderator",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            print(f"    Moderator role assigned")
        elif response.status_code == 400 and "already has" in response.text:
            print(f"    Already has moderator role")
        else:
            print(f"    Failed: {response.status_code} - {response.text}")

print("\nSetup complete!")
print(f"Created {len(created_users)} users")
print("\nUser credentials for locust:")
for user in created_users:
    role = "moderator" if created_users.index(user) % 3 == 0 else "user"
    print(f"  {user['email']} / {user['password']} [{role}]")