from app import db
from app.models.site import Site
from app.models.analysis import Analysis
from datetime import datetime, timedelta
from app.services.scraper import ScraperService
from app.services.content_extractor import ContentExtractor
from app.services.aeo_analyzer import AEOAnalyzer
import json

class AnalysisScheduler:
    @staticmethod
    def schedule_monthly_reanalysis():
        """
        Simulates checking sites that need re-analysis (older than 30 days).
        Returns a count of sites processed.
        """
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        # Find sites where last_analyzed is older than 30 days or never analyzed
        sites_to_reanalyze = Site.query.filter(
            (Site.last_analyzed <= one_month_ago) | (Site.last_analyzed == None)
        ).all()

        processed_count = 0
        for site in sites_to_reanalyze:
            success = AnalysisScheduler.reanalyze_site(site)
            if success:
                processed_count += 1
        
        return processed_count

    @staticmethod
    def reanalyze_site(site):
        """Logic to perform a single site re-analysis"""
        try:
            # 1. Scraping
            scraper = ScraperService()
            html, error = scraper.get_html(site.url)
            if error: return False

            # 2. Extract Content
            extractor = ContentExtractor(html)
            extracted_data = extractor.extract_all()

            # 3. AI Analysis
            ai_service = AEOAnalyzer()
            ai_result, ai_error = ai_service.analyze_content(extracted_data)
            if ai_error: return False

            # 4. Handle Versioning
            last_analysis = Analysis.query.filter_by(site_id=site.id).order_by(Analysis.version.desc()).first()
            new_version = (last_analysis.version + 1) if last_analysis else 1

            # 5. Create Analysis Record
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
            if extracted_data.get('title'):
                site.name = extracted_data['title']

            db.session.add(analysis)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error re-analyzing site {site.url}: {str(e)}")
            return False
