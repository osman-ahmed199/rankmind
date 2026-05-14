from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.subscription import Subscription
from app import db
from datetime import datetime, timedelta
import stripe

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/')
@login_required
def billing():
    # Get active subscription
    subscription = Subscription.query.filter_by(user_id=current_user.id, status='active').first()
    
    # Auto-create free subscription if missing
    if not subscription:
        subscription = Subscription(
            user_id=current_user.id,
            plan='free',
            status='active',
            expires_at=datetime.utcnow() + timedelta(days=3650) # 10 years for free plan
        )
        db.session.add(subscription)
        db.session.commit()
    
    plans = [
        {'id': 'free', 'name': 'المجانية', 'price': 0},
        {'id': 'pro', 'name': 'المحترفة', 'price': 29},
        {'id': 'enterprise', 'name': 'الشركات', 'price': 99}
    ]
    
    return render_template('billing/index.html', 
                           subscription=subscription,
                           current_plan=subscription.plan,
                           subscription_status=subscription.status,
                           plans=plans)

@billing_bp.route('/subscribe')
@login_required
def subscribe():
    plan = request.args.get('plan')
    if not plan:
        return redirect(url_for('billing.billing'))
    
    # Stripe Checkout Session placeholder
    flash(f'سيتم توجيهك إلى Stripe لإكمال الدفع لخطة {plan} قريباً.', 'info')
    return redirect(url_for('billing.billing'))

