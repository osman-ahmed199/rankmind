from app import create_app, db
from app.models.user import User
from app.models.site import Site
from app.models.analysis import Analysis
from app.models.subscription import Subscription

app = create_app()
with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("Done.")
