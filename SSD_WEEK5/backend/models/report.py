from extensions import db
from datetime import datetime
from models.user import User

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # email, phone, ip, social, web
    target = db.Column(db.String(255), nullable=False)  # email address, phone number, IP, etc.
    status = db.Column(db.String(20), nullable=False, default='processing')  # pending, processing, completed, failed
    result = db.Column(db.JSON)  # Store the intelligence results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Report {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'target': self.target,
            'status': self.status,
            'result': self.result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    user = db.relationship('User', backref=db.backref('reports', lazy=True)) 