import os
from dotenv import load_dotenv
load_dotenv()

# Set USE_SUPABASE to True by default
USE_SUPABASE = True

if USE_SUPABASE:
    db_user = os.getenv("SUPABASE_USER")
    db_pass = os.getenv("SUPABASE_PASSWORD")
    db_host = os.getenv("SUPABASE_HOST")
    db_name = os.getenv("SUPABASE_DB")
else:
    db_user = os.getenv("LOCAL_DB_USER")
    db_pass = os.getenv("LOCAL_DB_PASS")
    db_host = os.getenv("LOCAL_DB_HOST")
    db_name = os.getenv("LOCAL_DB_NAME")

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
