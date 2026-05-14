from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import stripe

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/')
@login_required
def billing():
    return render_template('billing/index.html')

@billing_bp.route('/subscribe')
@login_required
def subscribe():
    plan = request.args.get('plan')
    if not plan:
        return redirect(url_for('billing.billing'))
    
    # Stripe Checkout Session placeholder
    flash(f'سيتم توجيهك إلى Stripe لإكمال الدفع لخطة {plan} قريباً.', 'info')
    return redirect(url_for('billing.billing'))

