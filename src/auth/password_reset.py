from itsdangerous import URLSafeTimedSerializer
import os
from src.utils.redis_pool import get_redis
from datetime import timedelta

SECRET = os.getenv("SECRET_KEY", "change_me")
SALT = "password-reset-salt"
s = URLSafeTimedSerializer(SECRET)

def generate_reset_token(email: str) -> str:
    return s.dumps(email, salt=SALT)

def verify_reset_token(token: str, max_age: int = 3600) -> str:
    try:
        email = s.loads(token, salt=SALT, max_age=max_age)
    except Exception:
        return None
    return email
