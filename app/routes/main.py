from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return 'AEO Analyzer - Home Page'

@main_bp.route('/about')
def about():
    return 'About AEO Analyzer'
