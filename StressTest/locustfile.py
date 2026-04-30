from locust import HttpUser, task, between
import random
import uuid

TEST_USERS = [
    {"email": "test_user_0@test.com", "password": "Test123!", "role": "moderator"},
    {"email": "test_user_1@test.com", "password": "Test123!", "role": "user"},
    {"email": "test_user_2@test.com", "password": "Test123!", "role": "user"},
    {"email": "test_user_3@test.com", "password": "Test123!", "role": "moderator"},
    {"email": "test_user_4@test.com", "password": "Test123!", "role": "user"},
    {"email": "test_user_5@test.com", "password": "Test123!", "role": "user"},
    {"email": "test_user_6@test.com", "password": "Test123!", "role": "moderator"},
    {"email": "test_user_7@test.com", "password": "Test123!", "role": "user"},
    {"email": "test_user_8@test.com", "password": "Test123!", "role": "user"},
    {"email": "test_user_9@test.com", "password": "Test123!", "role": "moderator"},
]

class MixedUser(HttpUser):
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """Login and get token for each user"""
        self.user_data = random.choice(TEST_USERS)
        self.test_email = self.user_data["email"]
        self.test_password = self.user_data["password"]
        self.is_moderator = self.user_data["role"] == "moderator"
        
        response = self.client.post(
            "/v1/users/login",
            data={"username": self.test_email, "password": self.test_password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.auth_headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.auth_headers = {}
    
    # ==================== PUBLIC ENDPOINTS (no auth required) ====================
    
    @task(8)
    def get_defects_nearby(self):
        """GET /v1/defects/nearby/ - search defects in radius"""
        self.client.get(
            "/v1/defects/nearby/",
            params={
                "longitude": round(random.uniform(37.4, 37.8), 6),
                "latitude": round(random.uniform(55.5, 55.9), 6),
                "radius_meters": random.randint(50, 500)
            },
            name="/v1/defects/nearby"
        )
    
    @task(6)
    def get_defects_viewport(self):
        """GET /v1/defects/viewport/ - search defects in viewport"""
        min_lon = round(random.uniform(37.4, 37.6), 6)
        min_lat = round(random.uniform(55.5, 55.7), 6)
        self.client.get(
            "/v1/defects/viewport/",
            params={
                "min_longitude": min_lon,
                "min_latitude": min_lat,
                "max_longitude": round(min_lon + 0.2, 6),
                "max_latitude": round(min_lat + 0.2, 6),
                "limit": 100
            },
            name="/v1/defects/viewport"
        )
    
    @task(5)
    def get_defects_list(self):
        """GET /v1/defects - get defects with filters"""
        self.client.get(
            "/v1/defects",
            params={
                "limit": random.randint(10, 100),
                "offset": random.randint(0, 200)
            },
            name="/v1/defects"
        )
    
    @task(4)
    def snap_point(self):
        """POST /v1/snap-point - snap coordinates to road"""
        self.client.post(
            "/v1/snap-point",
            json={
                "longitude": round(random.uniform(37.4, 37.8), 6),
                "latitude": round(random.uniform(55.5, 55.9), 6),
                "max_distance_meters": 15
            },
            name="/v1/snap-point"
        )
    
    @task(3)
    def get_defect_by_id_random(self):
        """GET /v1/defects/{defect_id} - random UUID (will 404, but that's OK)"""
        random_uuid = str(uuid.uuid4())
        self.client.get(
            f"/v1/defects/{random_uuid}",
            name="/v1/defects/{defect_id}"
        )
    
    # ==================== AUTH ENDPOINTS (require token) ====================
    
    @task(5)
    def get_current_user(self):
        """GET /v1/users/me - get current user info"""
        if self.token:
            self.client.get("/v1/users/me", headers=self.auth_headers, name="/v1/users/me")
    
    @task(3)
    def get_pending_defects(self):
        """GET /v1/defects/pending/ - requires moderator role"""
        if self.token:
            self.client.get(
                "/v1/defects/pending/",
                headers=self.auth_headers,
                name="/v1/defects/pending"
            )
    
    @task(2)
    def get_defects_by_user_id(self):
        """GET /v1/users/{user_id}/defects - get defects of specific user"""
        if self.token:
            # Use current user's oid (would need to get it from /users/me first)
            # For load testing, use a placeholder (will 404 unless we have real ID)
            self.client.get(
                f"/v1/users/{uuid.uuid4()}/defects",
                headers=self.auth_headers,
                name="/v1/users/{user_id}/defects"
            )
    
    @task(2)
    def login(self):
        """POST /v1/users/login - authenticate"""
        self.client.post(
            "/v1/users/login",
            data={"username": self.test_email, "password": self.test_password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="/v1/users/login"
        )
    
    @task(2)
    def register_new_user(self):
        """POST /v1/users/register - create new user (may conflict, that's OK)"""
        random_suffix = random.randint(1, 1000000)
        self.client.post(
            "/v1/users/register",
            json={
                "email": f"locust_{random_suffix}@test.com",
                "password": "Test123!",
                "password_confirm": "Test123!"
            },
            name="/v1/users/register"
        )
    
    @task(1)
    def get_users_list(self):
        """GET /v1/users - admin only (will return 403 for regular users)"""
        if self.token:
            self.client.get(
                "/v1/users",
                params={"limit": 10, "offset": 0},
                headers=self.auth_headers,
                name="/v1/users"
            )
    
    # ==================== METRICS ====================
    
    @task(1)
    def metrics(self):
        """GET /metrics - Prometheus metrics"""
        self.client.get("/metrics", name="/metrics")


class DefectsOnlyUser(HttpUser):
    """Only public endpoints of Defects Service (no auth required)"""
    wait_time = between(0.5, 2)
    
    @task(10)
    def nearby(self):
        self.client.get(
            "/v1/defects/nearby/",
            params={"longitude": 37.6, "latitude": 55.6, "radius_meters": 100}
        )
    
    @task(7)
    def viewport(self):
        self.client.get(
            "/v1/defects/viewport/",
            params={
                "min_longitude": 37.5, "min_latitude": 55.5,
                "max_longitude": 37.7, "max_latitude": 55.7
            }
        )
    
    @task(5)
    def defects_list(self):
        self.client.get("/v1/defects", params={"limit": 50})
    
    @task(3)
    def snap_point(self):
        self.client.post(
            "/v1/snap-point",
            json={"longitude": 37.6, "latitude": 55.6, "max_distance_meters": 15}
        )
    
    @task(1)
    def metrics(self):
        self.client.get("/metrics")


class AuthOnlyUser(HttpUser):
    """Only endpoints that require authentication"""
    wait_time = between(1, 2)
    
    def on_start(self):
        self.user_data = random.choice([u for u in TEST_USERS if u["role"] != "moderator"])
        response = self.client.post(
            "/v1/users/login",
            data={"username": self.user_data["email"], "password": self.user_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.auth_headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(5)
    def get_current_user(self):
        self.client.get("/v1/users/me", headers=self.auth_headers)
    
    @task(3)
    def login(self):
        self.client.post(
            "/v1/users/login",
            data={"username": self.user_data["email"], "password": self.user_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    
    @task(2)
    def get_pending_defects(self):
        self.client.get("/v1/defects/pending/", headers=self.auth_headers)
    
    @task(1)
    def get_users(self):
        self.client.get("/v1/users", params={"limit": 10}, headers=self.auth_headers)