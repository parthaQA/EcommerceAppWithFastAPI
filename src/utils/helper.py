import hashlib
import secrets
import uuid

from fastapi import HTTPException, Request

from src.utils import settings
from src.utils.redis import redis_client
from src.utils.settings import Settings

class Helper:

    @staticmethod
    def generate_customer_id():
        return uuid.uuid4().hex[:10].upper()

    @staticmethod
    def generate_hashed_password(password: str):
        return hashlib.sha512(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return hashlib.sha512(password.encode()).hexdigest() == hashed_password

    
    @staticmethod
    def generate_cart_id():
        return str(secrets.choice(range(1000000, 9999999)))

    @staticmethod
    async def check_rate_limit(request: Request, mobile: str):

        setting = Settings()
        ip = request.client.host

        key = f"login:{mobile}:{ip}"

        count = await redis_client.get(key)

        print(f"Redis Key: {key}")
        print(f"Redis Count: {count}")
        print(f"Max Attempts: {setting.LOGIN_MAX_ATTEMPTS}")


        if count and int(count) >= setting.LOGIN_MAX_ATTEMPTS:
            raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again after {setting.LOGIN_LOCKOUT_MINUTES} minutes."
        )

    
    @staticmethod
    async def increment_login_attempt(request, mobile):

        setting = Settings()
        ip = request.client.host

        key = f"login:{mobile}:{ip}"

        count = await redis_client.incr(key)

        if count == 1:
            await redis_client.expire(
            key,
            setting.LOGIN_LOCKOUT_MINUTES * 60
        )

    
    @staticmethod
    async def clear_login_attempt(request, mobile):
        ip = request.client.host

        key = f"login:{mobile}:{ip}"

        await redis_client.delete(key)