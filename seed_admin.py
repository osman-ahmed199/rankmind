from app import create_app, db
from app.models.user import User
from app.models.subscription import Subscription
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # Create Admin User
    admin_email = 'osman@safeco-group.com'
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            password_hash=generate_password_hash('password123'),
            name='Osman Admin',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
    
    # Add/Update Free Subscription
    if not admin.subscription:
        sub = Subscription(
            user_id=admin.id,
            plan='free',
            expires_at=datetime.utcnow() + timedelta(days=365)
        )
        db.session.add(sub)
        db.session.commit()
    
    print(f"Admin user {admin_email} created successfully.")
