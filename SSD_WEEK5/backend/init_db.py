from app import create_app
from extensions import db
from models import Report, User

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully!") 