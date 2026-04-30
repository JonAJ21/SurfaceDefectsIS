#!/usr/bin/env python3
"""
locustfile.py — Нагрузочное тестирование с эмуляцией жизненного цикла сессии
Добавлены частые GET-запросы к Auth Service (профиль, сессии, роли, разрешения, список пользователей).
Запуск: locust -f locustfile.py --host http://localhost:80
"""

from locust import HttpUser, task, between, events
import random
import uuid
import logging
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# КОНФИГУРАЦИЯ
# ─────────────────────────────────────────────────────────────────────────────
API_HOST = "http://localhost:80"       # NGINX (маршрутизация /v1/*)
MINIO_HOST = "http://localhost:9000"   # MinIO для PMTiles
PMTILES_PATH = "/pmtiles/moscow_oblast.pmtiles"

CENTER_LAT, CENTER_LON = 55.752, 37.617
COORD_DELTA = 0.05

DEFECT_TYPES = [
    "longitudinal_crack", "transverse_crack", "alligator_crack",
    "repaired_crack", "pothole", "crosswalk_blur", "lane_line_blur",
    "manhole_cover", "patch", "rutting", "other"
]
SEVERITY_LEVELS = ["low", "medium", "high", "critical"]

# Параметры токенов
ACCESS_TOKEN_LIFETIME = 300        # 5 минут
REFRESH_BASE_INTERVAL = 180        # Базовый интервал проверки: 3 минуты
REFRESH_JITTER_RANGE = (60, 120)   # ±1–2 минуты случайного смещения
REFRESH_FAILURE_RATE = 0.05        # 5% рефрешей "падают" для эмуляции сетевых сбоев

# Загрузка предварительно зарегистрированных пользователей
def load_registered_users(filepath: str = "registered_users.txt") -> list:
    users = []
    path = Path(filepath)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                parts = line.split(":")
                if len(parts) >= 3:
                    users.append({
                        "email": parts[0], "password": parts[1],
                        "role": parts[2], "pre_registered": True
                    })
    return users

PRE_REGISTERED_USERS = load_registered_users()
if not PRE_REGISTERED_USERS:
    PRE_REGISTERED_USERS = [
        {"email": f"test_user_{i}@test.com", "password": "Test123!",
         "role": "moderator" if i % 5 == 0 else "user", "pre_registered": True}
        for i in range(20)
    ]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("locust")


def generate_range_request() -> dict:
    """Генерирует параметры для PMTiles Range-запроса"""
    if random.random() < 0.2:
        return {"range_header": "bytes=0-4095", "start": 0, "length": 4096}
    else:
        start = (random.randint(4096, 20_000_000) // 4096) * 4096
        length = random.choice([4096, 8192, 16384])
        return {"range_header": f"bytes={start}-{start + length - 1}", "start": start, "length": length}


# ─────────────────────────────────────────────────────────────────────────────
# БАЗОВЫЙ КЛАСС С ПОЛНОЙ ЭМУЛЯЦИЕЙ СЕССИИ + РЕФРЕШ
# ─────────────────────────────────────────────────────────────────────────────
class SessionUser(HttpUser):
    abstract = True
    wait_time = between(0.5, 2.0)
    
    def on_start(self):
        """Инициализация сессии — вызывается ОДИН РАЗ при старте"""
        self.token: str | None = None
        self.refresh_token: str | None = None
        self.token_expires_at: datetime | None = None
        self.auth_headers: dict = {}
        self.user_role: str | None = None
        self.user_email: str | None = None
        self.is_authenticated: bool = False
        self._auth_completed: bool = False
        
        self._refresh_count = 0
        self._relogin_count = 0
        self._auth_failures = 0
        
        user_jitter = random.randint(*REFRESH_JITTER_RANGE)
        self.next_refresh_check = datetime.now() + timedelta(seconds=REFRESH_BASE_INTERVAL + user_jitter)
        
        self._pick_user()
        self._authenticate_session()
    
    def _pick_user(self):
        if PRE_REGISTERED_USERS and random.random() < 0.7:
            user = random.choice(PRE_REGISTERED_USERS).copy()
            self.is_new_user = False
        else:
            user = {
                "email": f"locust_{uuid.uuid4().hex[:10]}@test.com",
                "password": "Test123!",
                "role": random.choice(["user", "moderator"]),
                "pre_registered": False
            }
            self.is_new_user = True
        self.user_email = user["email"]
        self.user_password = user["password"]
        self.user_role = user["role"]
    
    def _authenticate_session(self):
        if self._auth_completed: return
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if self.is_new_user:
                    resp = self.client.post(
                        "/v1/users/register",
                        json={"email": self.user_email, "password": self.user_password,
                              "password_confirm": self.user_password},
                        name="/v1/users/register", timeout=10
                    )
                    if resp.status_code not in (200, 201, 409):
                        logger.warning(f"Registration failed ({resp.status_code}): {self.user_email}")
                
                if self._login():
                    self.is_authenticated = True
                    self._auth_completed = True
                    logger.info(f"✓ Session started: {self.user_email} ({self.user_role})")
                    events.request.fire(request_type="AUTH", name="session_started", response_time=0, response_length=0, response=None, exception=None)
                    return
                else:
                    self._auth_failures += 1
                    logger.warning(f"Login attempt {attempt+1} failed for {self.user_email}")
                    time.sleep(0.3)
            except Exception as e:
                logger.error(f"Auth error: {e}")
                time.sleep(0.3)
        logger.error(f"✗ Failed to authenticate {self.user_email}")
        self.is_authenticated = False
    
    def _login(self) -> bool:
        try:
            resp = self.client.post(
                "/v1/users/login",
                data={"username": self.user_email, "password": self.user_password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="/v1/users/login", timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.token_expires_at = datetime.now() + timedelta(seconds=ACCESS_TOKEN_LIFETIME)
                self.auth_headers = {"Authorization": f"Bearer {self.token}"}
                return True
            else:
                logger.warning(f"Login failed ({resp.status_code}): {self.user_email} | {resp.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"Login exception: {e}")
            return False
    
    def _refresh_tokens(self) -> bool:
        if not self.refresh_token: return False
        if random.random() < REFRESH_FAILURE_RATE:
            logger.debug(f"~ Simulated refresh failure for {self.user_email}")
            return False
        try:
            resp = self.client.post(
                "/v1/users/me/refresh",
                data={"refresh_token": self.refresh_token},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="/v1/users/me/refresh", timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.token_expires_at = datetime.now() + timedelta(seconds=ACCESS_TOKEN_LIFETIME)
                self.auth_headers = {"Authorization": f"Bearer {self.token}"}
                self._refresh_count += 1
                logger.debug(f"✓ Tokens refreshed: {self.user_email}")
                events.request.fire(request_type="AUTH", name="token_refreshed", response_time=resp.elapsed.total_seconds() * 1000, response_length=len(resp.content), response=resp, exception=None)
                return True
            else:
                logger.warning(f"Refresh failed ({resp.status_code}): {self.user_email}")
                return False
        except Exception as e:
            logger.error(f"Refresh exception: {e}")
            return False
    
    def _ensure_auth(self) -> bool:
        if not self.is_authenticated: return False
        if not self.token: return self._login()
        if self.token_expires_at:
            time_until_expiry = (self.token_expires_at - datetime.now()).total_seconds()
            if time_until_expiry < 60:
                logger.debug(f"Token expiring soon, refreshing...")
                if not self._refresh_tokens():
                    logger.debug(f"Refresh failed, attempting re-login...")
                    if not self._login():
                        self._auth_failures += 1
                        self.is_authenticated = False
                        events.request.fire(request_type="AUTH", name="auth_failed", response_time=0, response_length=0, response=None, exception=Exception("Re-login failed"))
                        return False
                    else:
                        self._relogin_count += 1
                        logger.info(f"✓ Re-logged in: {self.user_email}")
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}
        return True
    
    @task(1)
    def _background_auth_check(self):
        if not self.is_authenticated: return
        now = datetime.now()
        if now < self.next_refresh_check: return
        logger.debug(f"~ Periodic refresh check for {self.user_email}")
        if not self._refresh_tokens(): self._login()
        new_jitter = random.randint(*REFRESH_JITTER_RANGE)
        self.next_refresh_check = now + timedelta(seconds=REFRESH_BASE_INTERVAL + new_jitter)
    
    def _request_pmtiles(self, range_info: dict):
        url = f"{MINIO_HOST}{PMTILES_PATH}"
        try:
            resp = requests.get(url, headers={"Range": range_info["range_header"]}, timeout=10)
            status_ok = resp.status_code in (200, 206)
            events.request.fire(request_type="GET", name="/pmtiles [Range]", response_time=resp.elapsed.total_seconds() * 1000, response_length=resp.status_code == 206 and range_info["length"] or len(resp.content), response=resp, exception=None if status_ok else Exception(f"Status {resp.status_code}"))
        except Exception as e:
            events.request.fire(request_type="GET", name="/pmtiles [Range]", response_time=0, response_length=0, response=None, exception=e)


# ─────────────────────────────────────────────────────────────────────────────
# СЦЕНАРИЙ 1: ВОДИТЕЛЬ (80% трафика) + ЧАСТЫЕ ЗАПРОСЫ К AUTH SERVICE
# ─────────────────────────────────────────────────────────────────────────────
class DriverUser(SessionUser):
    weight = 80
    
    @task(40)
    def fetch_pmtiles_tile(self):
        self._request_pmtiles(generate_range_request())
    
    @task(12)
    def get_defects_viewport(self):
        if not self._ensure_auth(): return
        min_lon = round(random.uniform(CENTER_LON - COORD_DELTA, CENTER_LON + COORD_DELTA), 6)
        min_lat = round(random.uniform(CENTER_LAT - COORD_DELTA, CENTER_LAT + COORD_DELTA), 6)
        self.client.get("/v1/defects/viewport/", params={
            "min_longitude": min_lon, "min_latitude": min_lat,
            "max_longitude": round(min_lon + 0.03, 6), "max_latitude": round(min_lat + 0.03, 6), "limit": 100
        }, headers=self.auth_headers, name="/v1/defects/viewport")
    
    @task(12)
    def get_defects_list(self):
        if not self._ensure_auth(): return
        limit = random.choice([20, 50, 100])
        offset = random.randint(0, 5) * limit
        params = {"limit": limit, "offset": offset}
        if random.random() < 0.3: params["defect_types"] = random.choice(DEFECT_TYPES)
        if random.random() < 0.2: params["min_severity"] = random.choice(SEVERITY_LEVELS)
        self.client.get("/v1/defects", params=params, headers=self.auth_headers, name="/v1/defects")
    
    @task(8)
    def get_defects_nearby(self):
        if not self._ensure_auth(): return
        lat = round(random.uniform(CENTER_LAT - COORD_DELTA, CENTER_LAT + COORD_DELTA), 6)
        lon = round(random.uniform(CENTER_LON - COORD_DELTA, CENTER_LON + COORD_DELTA), 6)
        self.client.get("/v1/defects/nearby/", params={
            "latitude": lat, "longitude": lon, "radius_meters": random.choice([100, 250, 500])
        }, headers=self.auth_headers, name="/v1/defects/nearby")
    
    # 🔑 НОВЫЕ ЗАПРОСЫ К AUTH SERVICE (ВОДИТЕЛЬ)
    @task(6)
    def get_current_user_profile(self):
        """GET /v1/users/me — профиль пользователя"""
        if not self._ensure_auth(): return
        self.client.get("/v1/users/me", headers=self.auth_headers, name="/v1/users/me")
    
    @task(4)
    def get_current_user_sessions(self):
        """GET /v1/users/me/session — активные сессии"""
        if not self._ensure_auth(): return
        self.client.get("/v1/users/me/session", headers=self.auth_headers, name="/v1/users/me/session")
    
    @task(3)
    def get_permissions_list(self):
        """GET /v1/permissions — список разрешений"""
        if not self._ensure_auth(): return
        self.client.get("/v1/permissions", params={"limit": 20, "offset": 0}, headers=self.auth_headers, name="/v1/permissions")
    
    @task(3)
    def snap_point(self):
        if not self._ensure_auth(): return
        self.client.post("/v1/snap-point", json={
            "longitude": round(random.uniform(CENTER_LON - COORD_DELTA, CENTER_LON + COORD_DELTA), 6),
            "latitude": round(random.uniform(CENTER_LAT - COORD_DELTA, CENTER_LAT + COORD_DELTA), 6),
            "max_distance_meters": 15
        }, headers=self.auth_headers, name="/v1/snap-point")


# ─────────────────────────────────────────────────────────────────────────────
# СЦЕНАРИЙ 2: МОДЕРАТОР (15% трафика) + РАСШИРЕННЫЕ ЗАПРОСЫ К AUTH
# ─────────────────────────────────────────────────────────────────────────────
class ModeratorUser(SessionUser):
    weight = 15
    
    @task(25)
    def fetch_pmtiles_tile(self):
        self._request_pmtiles(generate_range_request())
    
    @task(18)
    def get_defects_list(self):
        if not self._ensure_auth(): return
        limit = random.choice([20, 50, 100])
        offset = random.randint(0, 3) * limit
        self.client.get("/v1/defects", params={
            "limit": limit, "offset": offset, "defect_statuses": "pending"
        }, headers=self.auth_headers, name="/v1/defects")
    
    @task(12)
    def moderate_defect(self):
        if not self._ensure_auth() or self.user_role != "moderator": return
        defect_id = str(uuid.uuid4())
        status = random.choice(["approved", "rejected"])
        reason = "Не соответствует ГОСТ Р 50597-2017" if status == "rejected" else None
        self.client.patch(f"/v1/defects/{defect_id}/moderate", params={
            "status": status, "rejection_reason": reason
        }, headers=self.auth_headers, name="/v1/defects/{id}/moderate")
    
    @task(8)
    def get_defects_viewport(self):
        if not self._ensure_auth(): return
        min_lon = round(random.uniform(CENTER_LON - 0.02, CENTER_LON + 0.02), 6)
        min_lat = round(random.uniform(CENTER_LAT - 0.02, CENTER_LAT + 0.02), 6)
        self.client.get("/v1/defects/viewport/", params={
            "min_longitude": min_lon, "min_latitude": min_lat,
            "max_longitude": min_lon + 0.04, "max_latitude": min_lat + 0.04, "limit": 100
        }, headers=self.auth_headers, name="/v1/defects/viewport")
    
    # 🔑 НОВЫЕ ЗАПРОСЫ К AUTH SERVICE (МОДЕРАТОР/АДМИН)
    @task(5)
    def get_users_list(self):
        """GET /v1/users — список пользователей"""
        if not self._ensure_auth(): return
        self.client.get("/v1/users", params={"limit": 20, "offset": 0}, headers=self.auth_headers, name="/v1/users")
    
    @task(4)
    def get_roles_list(self):
        """GET /v1/roles — список ролей"""
        if not self._ensure_auth(): return
        self.client.get("/v1/roles", params={"limit": 20, "offset": 0}, headers=self.auth_headers, name="/v1/roles")
    
    @task(3)
    def get_current_user_sessions(self):
        """GET /v1/users/me/session — активные сессии"""
        if not self._ensure_auth(): return
        self.client.get("/v1/users/me/session", headers=self.auth_headers, name="/v1/users/me/session")
    
    @task(3)
    def get_permissions_list(self):
        """GET /v1/permissions — список разрешений"""
        if not self._ensure_auth(): return
        self.client.get("/v1/permissions", params={"limit": 20, "offset": 0}, headers=self.auth_headers, name="/v1/permissions")


# ─────────────────────────────────────────────────────────────────────────────
# СЦЕНАРИЙ 3: АНОНИМНЫЙ ПОЛЬЗОВАТЕЛЬ (5% трафика)
# ─────────────────────────────────────────────────────────────────────────────
class AnonymousUser(HttpUser):
    weight = 5
    wait_time = between(0.5, 2.0)
    
    @task(50)
    def fetch_pmtiles_tile(self):
        self._request_pmtiles(generate_range_request())
    
    @task(20)
    def get_defects_viewport(self):
        min_lon = round(random.uniform(CENTER_LON - COORD_DELTA, CENTER_LON + COORD_DELTA), 6)
        min_lat = round(random.uniform(CENTER_LAT - COORD_DELTA, CENTER_LAT + COORD_DELTA), 6)
        self.client.get("/v1/defects/viewport/", params={
            "min_longitude": min_lon, "min_latitude": min_lat,
            "max_longitude": min_lon + 0.03, "max_latitude": min_lat + 0.03, "limit": 100
        }, name="/v1/defects/viewport")
    
    @task(15)
    def get_defects_list(self):
        limit = random.choice([20, 50, 100])
        offset = random.randint(0, 3) * limit
        self.client.get("/v1/defects", params={"limit": limit, "offset": offset}, name="/v1/defects")
    
    @task(10)
    def get_defects_nearby(self):
        lat = round(random.uniform(CENTER_LAT - COORD_DELTA, CENTER_LAT + COORD_DELTA), 6)
        lon = round(random.uniform(CENTER_LON - COORD_DELTA, CENTER_LON + COORD_DELTA), 6)
        self.client.get("/v1/defects/nearby/", params={
            "latitude": lat, "longitude": lon, "radius_meters": 200
        }, name="/v1/defects/nearby")
    
    def _request_pmtiles(self, range_info: dict):
        url = f"{MINIO_HOST}{PMTILES_PATH}"
        try:
            resp = requests.get(url, headers={"Range": range_info["range_header"]}, timeout=10)
            status_ok = resp.status_code in (200, 206)
            events.request.fire(request_type="GET", name="/pmtiles [Range]", response_time=resp.elapsed.total_seconds() * 1000, response_length=resp.status_code == 206 and range_info["length"] or len(resp.content), response=resp, exception=None if status_ok else Exception(f"Status {resp.status_code}"))
        except Exception as e:
            events.request.fire(request_type="GET", name="/pmtiles [Range]", response_time=0, response_length=0, response=None, exception=e)


# ─────────────────────────────────────────────────────────────────────────────
# ОБРАБОТЧИКИ СОБЫТИЙ
# ─────────────────────────────────────────────────────────────────────────────
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logger.info("🚀 Load test started — auth lifecycle + extended Auth GET requests enabled")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    total_refreshes = sum(getattr(u, "_refresh_count", 0) for u in environment.runner.user_classes)
    total_relogins = sum(getattr(u, "_relogin_count", 0) for u in environment.runner.user_classes)
    total_failures = sum(getattr(u, "_auth_failures", 0) for u in environment.runner.user_classes)
    logger.info(f"📊 Auth stats: refreshes={total_refreshes}, relogins={total_relogins}, failures={total_failures}")