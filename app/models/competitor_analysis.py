from app import db
from datetime import datetime

class CompetitorAnalysis(db.Model):
    __tablename__ = 'competitor_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_site_url = db.Column(db.String(500), nullable=False)
    competitor_urls = db.Column(db.Text)  # JSON list of urls
    result = db.Column(db.Text)  # AI output JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('competitor_analyses', lazy=True))
