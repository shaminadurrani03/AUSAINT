from extensions import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # email, phone, ip, social, web
    target = db.Column(db.String(255), nullable=False)  # email address, phone number, IP, etc.
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    result = db.Column(db.JSON)  # Store the intelligence results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('reports', lazy=True)) 