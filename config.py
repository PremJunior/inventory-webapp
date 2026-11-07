import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-change-me")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "instance/inventory.db")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_SECURE = True

class TestConfig(Config):
    TESTING = True
    DATABASE_PATH = "instance/test.db"
