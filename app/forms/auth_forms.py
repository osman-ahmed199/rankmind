from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app.models.user import User

class RegistrationForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Length(min=2, max=100, message='يجب أن يكون الاسم بين 2 و 100 حرف')
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Email(message='بريد إلكتروني غير صحيح')
    ])
    company_name = StringField('اسم الشركة (اختياري)', validators=[
        Length(max=200, message='اسم الشركة طويل جداً')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Length(min=6, message='يجب أن تكون كلمة المرور 6 أحرف على الأقل')
    ])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        EqualTo('password', message='كلمات المرور غير متطابقة')
    ])
    submit = SubmitField('تسجيل')

class LoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Email(message='بريد إلكتروني غير صحيح')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='هذا الحقل مطلوب')
    ])
    submit = SubmitField('دخول')
