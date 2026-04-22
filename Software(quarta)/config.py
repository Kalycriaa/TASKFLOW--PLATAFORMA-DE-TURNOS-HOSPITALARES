import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///hospital.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

    LOCATION_PROVIDER = os.getenv("LOCATION_PROVIDER", "manual")
    REGIONAL_GEO_API_URL = os.getenv("REGIONAL_GEO_API_URL", "")
    REGIONAL_DISTANCE_API_URL = os.getenv("REGIONAL_DISTANCE_API_URL", "")
    REGIONAL_API_KEY = os.getenv("REGIONAL_API_KEY", "")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
