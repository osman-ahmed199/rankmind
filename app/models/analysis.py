from app import db
from datetime import datetime

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')
    result = db.Column(db.Text)
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    version = db.Column(db.Integer, default=1)
    previous_analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=True)
    
    previous_analysis = db.relationship('Analysis', remote_side=[id])
