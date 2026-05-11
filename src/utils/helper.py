import hashlib
import uuid

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