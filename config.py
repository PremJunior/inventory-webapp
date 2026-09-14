import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-change-me")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "instance/inventory.db")


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    DATABASE_PATH = "instance/test.db"
