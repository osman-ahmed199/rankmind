from flask import Blueprint, render_template, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.site import Site
from app.models.analysis import Analysis
from app.services.scheduler import AnalysisScheduler
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard/index.html')

@dashboard_bp.route('/history/<int:site_id>')
@login_required
def site_history(site_id):
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id and not current_user.is_admin:
        flash('غير مسموح لك بعرض هذا التاريخ.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    analyses = Analysis.query.filter_by(site_id=site.id).order_by(Analysis.analysis_date.desc()).all()
    return render_template('dashboard/history.html', site=site, analyses=analyses)

@dashboard_bp.route('/compare/<int:analysis_id>')
@login_required
def compare_analysis(analysis_id):
    current_analysis = Analysis.query.get_or_404(analysis_id)
    site = Site.query.get(current_analysis.site_id)
    
    if site.user_id != current_user.id and not current_user.is_admin:
        flash('غير مسموح لك بالمقارنة.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    prev_analysis = None
    if current_analysis.previous_analysis_id:
        prev_analysis = Analysis.query.get(current_analysis.previous_analysis_id)
    
    current_data = json.loads(current_analysis.result)
    prev_data = json.loads(prev_analysis.result) if prev_analysis else None
    
    return render_template('dashboard/compare.html', 
                           site=site, 
                           current=current_analysis, 
                           prev=prev_analysis,
                           current_data=current_data,
                           prev_data=prev_data)

@dashboard_bp.route('/api/site/<int:site_id>/history')
@login_required
def api_site_history(site_id):
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    analyses = Analysis.query.filter_by(site_id=site.id).order_by(Analysis.analysis_date.asc()).all()
    
    history_data = []
    for a in analyses:
        res = json.loads(a.result)
        history_data.append({
            'date': a.analysis_date.strftime('%Y-%m-%d'),
            'score': a.score,
            'breakdown': res.get('breakdown', {})
        })
    
    return jsonify(history_data)

@dashboard_bp.route('/reanalyze-all')
@login_required
def reanalyze_all():
    if not current_user.is_admin:
        flash('هذا الإجراء للمسؤولين فقط.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    count = AnalysisScheduler.schedule_monthly_reanalysis()
    flash(f'تمت معالجة {count} موقع وإعادة تحليلهم بنجاح.', 'success')
    return redirect(url_for('dashboard.dashboard'))

