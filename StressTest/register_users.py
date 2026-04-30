#!/usr/bin/env python3
"""
register_users.py — Предварительная регистрация тестовых пользователей
Запуск: python register_users.py --host http://localhost:80 --count 50
"""

import argparse
import uuid
import requests
import sys
import time
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# КОНФИГУРАЦИЯ
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_HOST = "http://localhost:80"
DEFAULT_COUNT = 50
DEFAULT_PASSWORD = "Test123!"
ROLES = ["user", "moderator"]
ROLE_WEIGHTS = [0.8, 0.2]  # 80% обычных пользователей, 20% модераторов


def register_user(base_url: str, email: str, password: str, role: str) -> bool:
    """Регистрирует одного пользователя"""
    try:
        # 1. Регистрация
        resp = requests.post(
            f"{base_url}/v1/users/register",
            json={
                "email": email,
                "password": password,
                "password_confirm": password
            },
            timeout=10
        )
        
        if resp.status_code in (200, 201):
            print(f"✓ Registered: {email} ({role})")
            return True
        elif resp.status_code == 409:
            print(f"~ Already exists: {email}")
            return True  # Нормально при повторном запуске
        else:
            print(f"✗ Failed {resp.status_code}: {email} | {resp.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection refused: {base_url}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Pre-register test users")
    parser.add_argument("--host", default=DEFAULT_HOST, help="API base URL")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT, help="Number of users to register")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Default password for all users")
    parser.add_argument("--prefix", default="test_user", help="Email prefix")
    parser.add_argument("--domain", default="test.com", help="Email domain")
    args = parser.parse_args()
    
    print(f"🚀 Registering {args.count} users at {args.host}")
    print(f"📧 Format: {args.prefix}_N@{args.domain}")
    print(f"🔑 Password: {args.password}")
    print("-" * 60)
    
    success_count = 0
    start_time = time.time()
    
    for i in range(args.count):
        # Генерируем пользователя
        email = f"{args.prefix}_{i}@{args.domain}"
        role = "moderator" if i % 5 == 0 else "user"  # Каждый 5-й — модератор
        
        if register_user(args.host, email, args.password, role):
            success_count += 1
        
        # Небольшая пауза, чтобы не перегружать сервер
        time.sleep(0.1)
    
    elapsed = time.time() - start_time
    print("-" * 60)
    print(f"✅ Done: {success_count}/{args.count} users registered in {elapsed:.2f}s")
    
    # Сохраняем список для использования в locustfile
    with open("registered_users.txt", "w") as f:
        f.write("# Format: email:password:role\n")
        for i in range(args.count):
            email = f"{args.prefix}_{i}@{args.domain}"
            role = "moderator" if i % 5 == 0 else "user"
            f.write(f"{email}:{args.password}:{role}\n")
    
    print(f"📄 Saved user list to: registered_users.txt")
    return 0 if success_count == args.count else 1


if __name__ == "__main__":
    sys.exit(main())