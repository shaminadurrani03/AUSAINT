import os
from dotenv import load_dotenv
load_dotenv()

# Set USE_SUPABASE to False to use SQLite
USE_SUPABASE = False

if USE_SUPABASE:
    db_user = os.getenv("SUPABASE_USER")
    db_pass = os.getenv("SUPABASE_PASSWORD")
    db_host = os.getenv("SUPABASE_HOST")
    db_name = os.getenv("SUPABASE_DB")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"
else:
    # Use SQLite for local development
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"

class Config:
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "dev-jwt-secret")
