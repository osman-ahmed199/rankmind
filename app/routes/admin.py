from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from app.models.site import Site
from app.models.analysis import Analysis
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('غير مسموح لك بالدخول لهذه الصفحة.', 'error')
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    users_count = User.query.count()
    sites_count = Site.query.count()
    analyses_count = Analysis.query.count()
    return render_template('admin/dashboard.html', 
                           users_count=users_count, 
                           sites_count=sites_count, 
                           analyses_count=analyses_count)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/sites')
@login_required
@admin_required
def sites():
    all_sites = Site.query.all()
    return render_template('admin/sites.html', sites=all_sites)
