from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
import sys

def change_password(email, new_password):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"--- SUCCESS ---")
            print(f"تم تغيير كلمة مرور المستخدم {email} بنجاح.")
        else:
            print(f"--- ERROR ---")
            print(f"المستخدم {email} غير موجود في قاعدة البيانات.")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        change_password(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python update_password.py [email] [new_password]")
