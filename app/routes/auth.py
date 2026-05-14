from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.user import User
from app.models.subscription import Subscription
from app.forms.auth_forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('البريد الإلكتروني مسجل بالفعل.', 'error')
            return render_template('auth/register.html', form=form)
            
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            email=form.email.data,
            password_hash=hashed_password,
            name=form.full_name.data,
            company_name=form.company_name.data
        )
        db.session.add(user)
        db.session.commit()
        
        subscription = Subscription(
            user_id=user.id,
            plan='free',
            status='active'
        )
        db.session.add(subscription)
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح! يمكنك الدخول الآن.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('تم تسجيل الدخول بنجاح!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.dashboard'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('main.index'))
