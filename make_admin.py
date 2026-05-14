from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Make osman@safeco-group.com an admin
    user = User.query.filter_by(email='osman@safeco-group.com').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"User {user.email} is now an admin.")
    else:
        # Check other users if osman doesn't exist
        user = User.query.first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f"User {user.email} is now an admin (Fallback).")
        else:
            print("No users found in database.")
