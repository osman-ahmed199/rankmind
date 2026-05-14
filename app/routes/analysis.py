from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app import db
from app.models.site import Site
from app.models.analysis import Analysis
from app.services.scraper import ScraperService
from app.services.content_extractor import ContentExtractor
from app.services.aeo_analyzer import AEOAnalyzer
from app.services.score_calculator import ScoreCalculator
import json
from datetime import datetime
from urllib.parse import urlparse

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/start', methods=['POST'])
@login_required
def start_analysis():
    url = request.form.get('url', '').strip()
    if not url:
        flash('يرجى إدخال رابط الموقع.', 'error')
        return redirect(url_for('dashboard.dashboard'))

    # Clean URL and extract domain for naming
    parsed_url = urlparse(url)
    domain = parsed_url.netloc if parsed_url.netloc else parsed_url.path.split('/')[0]
    if not domain and parsed_url.path:
        domain = parsed_url.path
    
    # Remove www. for cleaner display
    domain = domain.replace('www.', '')

    # Check Free Tier Limit (1 site only)
    user_sites_count = Site.query.filter_by(user_id=current_user.id).count()
    existing_site = Site.query.filter_by(user_id=current_user.id, url=url).first()
    
    if user_sites_count >= 1 and not existing_site:
        if current_user.subscription.plan == 'free':
            flash('الخطة المجانية تسمح بموقع واحد فقط. يرجى الترقية لتحليل مواقع أكثر.', 'error')
            return redirect(url_for('dashboard.dashboard'))

    # Add or update site
    if not existing_site:
        site = Site(user_id=current_user.id, url=url, name=domain)
        db.session.add(site)
        db.session.commit()
    else:
        site = existing_site

    # Start Scraping
    scraper = ScraperService()
    html, error = scraper.get_html(url)
    
    if error:
        flash(error, 'error')
        return redirect(url_for('dashboard.dashboard'))

    # Extract Content
    extractor = ContentExtractor(html)
    extracted_data = extractor.extract_all()
    
    # AI Analysis
    ai_service = AEOAnalyzer()
    try:
        ai_result, ai_error = ai_service.analyze_content(extracted_data)
    except Exception as e:
        print(f"CRITICAL ROUTE ERROR: {str(e)}")
        flash(f"حدث خطأ تقني في التحليل: {str(e)}", 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    if ai_error:
        flash(ai_error, 'error')
        return redirect(url_for('dashboard.dashboard'))

    # Update site name if title found
    if extracted_data.get('title'):
        site.name = extracted_data['title']

    # Handle Versioning
    last_analysis = Analysis.query.filter_by(site_id=site.id).order_by(Analysis.version.desc()).first()
    new_version = (last_analysis.version + 1) if last_analysis else 1

    # Create Analysis record
    analysis = Analysis(
        site_id=site.id,
        status='completed',
        result=json.dumps(ai_result, ensure_ascii=False),
        score=ai_result.get('overall_score', 0),
        completed_at=datetime.utcnow(),
        analysis_date=datetime.utcnow(),
        version=new_version,
        previous_analysis_id=last_analysis.id if last_analysis else None
    )
    
    site.last_analyzed = datetime.utcnow()
    db.session.add(analysis)
    db.session.commit()

    flash('تم تحليل الموقع بالذكاء الاصطناعي بنجاح!', 'success')
    return redirect(url_for('analysis.view_result', analysis_id=analysis.id))

@analysis_bp.route('/result/<int:analysis_id>')
@login_required
def view_result(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    if analysis.site.user_id != current_user.id:
        flash('غير مسموح لك بعرض هذا التحليل.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    result_data = json.loads(analysis.result)
    grade = ScoreCalculator.get_grade(analysis.score)
    
    return render_template('dashboard/analysis_result.html', 
                           analysis=analysis, 
                           data=result_data, 
                           grade=grade)

@analysis_bp.route('/')
@login_required
def analysis():
    return redirect(url_for('dashboard.dashboard'))

@analysis_bp.route('/new')
@login_required
def new_analysis():
    return render_template('analysis/new.html')

