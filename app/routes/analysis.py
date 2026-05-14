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
import traceback
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
    try:
        # Check if ID exists, otherwise return 404
        analysis = Analysis.query.get_or_404(analysis_id)
        
        if analysis.site.user_id != current_user.id:
            flash('غير مسموح لك بعرض هذا التحليل.', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        # Fallback structure if analysis result is empty or None
        fallback = {
            "overall_score": 0, 
            "breakdown": {}, 
            "issues": [], 
            "action_plan": [], 
            "ai_summary": "حدث خطأ في التحليل أو النتيجة غير متوفرة حالياً."
        }
        
        try:
            if analysis.result:
                result_data = json.loads(analysis.result)
            else:
                result_data = fallback
        except (json.JSONDecodeError, TypeError):
            result_data = fallback
            
        grade = ScoreCalculator.get_grade(analysis.score or 0)
        
        return render_template('dashboard/analysis_result.html', 
                            analysis=analysis, 
                            data=result_data, 
                            grade=grade)
    except Exception as e:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@analysis_bp.route('/report/<uuid>')
def public_report(uuid):
    analysis = Analysis.query.filter_by(uuid=uuid, is_public=True).first_or_404()
    
    result_data = json.loads(analysis.result)
    grade = ScoreCalculator.get_grade(analysis.score)
    
    return render_template('dashboard/public_report.html', 
                           analysis=analysis, 
                           data=result_data, 
                           grade=grade)

@analysis_bp.route('/report/<uuid>/download')
def download_pdf(uuid):
    try:
        analysis = Analysis.query.filter_by(uuid=uuid).first_or_404()
        
        # Check permission if not public
        if not analysis.is_public:
            if not current_user.is_authenticated or analysis.site.user_id != current_user.id:
                flash('غير مسموح لك بتحميل هذا التقرير.', 'error')
                return redirect(url_for('main.index'))

        from app.services.pdf_generator import PDFGenerator
        pdf_service = PDFGenerator()
        pdf_content = pdf_service.generate_report(analysis)
        
        from flask import make_response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=RankMind-Report-{analysis.site.name}.pdf'
        return response
    except Exception as e:
        print(f"PDF ERROR: {str(e)}")
        flash(f'حدث خطأ أثناء توليد ملف PDF: {str(e)}', 'error')
        return redirect(url_for('dashboard.dashboard'))

@analysis_bp.route('/compare', methods=['GET', 'POST'])
@login_required
def compare():
    if request.method == 'POST':
        user_url = request.form.get('user_url')
        comp1 = request.form.get('comp1')
        comp2 = request.form.get('comp2')
        comp3 = request.form.get('comp3')
        
        competitors = [c for c in [comp1, comp2, comp3] if c and c.strip()]
        
        if not user_url or not competitors:
            flash('يرجى إدخال رابط موقعك ومنافس واحد على الأقل.', 'error')
            return render_template('dashboard/compare_competitors.html')
            
        from app.services.competitor_analyzer import CompetitorAnalyzer
        from app.models.competitor_analysis import CompetitorAnalysis
        
        analyzer = CompetitorAnalyzer()
        result, error = analyzer.analyze_competition(user_url, competitors)
        
        if error:
            flash(f'حدث خطأ في التحليل: {error}', 'error')
            return render_template('dashboard/compare_competitors.html')
            
        # Save to DB
        comp_analysis = CompetitorAnalysis(
            user_id=current_user.id,
            user_site_url=user_url,
            competitor_urls=json.dumps(competitors),
            result=json.dumps(result)
        )
        db.session.add(comp_analysis)
        db.session.commit()
        
        return render_template('dashboard/compare_competitors.html', result=result)
        
    return render_template('dashboard/compare_competitors.html')

@analysis_bp.route('/')
@login_required
def analysis():
    return redirect(url_for('dashboard.dashboard'))

@analysis_bp.route('/new')
@login_required
def new_analysis():
    return render_template('analysis/new.html')

