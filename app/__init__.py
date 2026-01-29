import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from app.main.utilities import get_category_color,get_category_icon

load_dotenv()

from config import Config, DevelopmentConfig, ProductionConfig
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
cache = Cache()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Select config based on environment
    if config_class is None:
        env = os.getenv('FLASK_ENV', 'production')
        config_class = DevelopmentConfig if env == 'development' else ProductionConfig
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    app.jinja_env.add_extension('jinja2.ext.do')
    csrf.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Create instance folder
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Register blueprints
    from app.main.routes import main
    from app.transactions.routes import transactions
    from app.users.routes import users
    
    app.register_blueprint(main)
    app.register_blueprint(transactions)
    app.register_blueprint(users)
    
    # Before request - disable caching for all pages
    @app.before_request
    def before_request():
        # Set session cookie as non-persistent to force logout on browser close
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(401)
    def unauthorized(error):
        return render_template('401.html'), 401

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return render_template('500.html'), 500
    
    # Security headers and cache control
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Always prevent caching for authenticated requests
        from flask_login import current_user
        if current_user.is_authenticated:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            response.headers['Date'] = None
        else:
            # For public pages, allow some caching
            response.headers['Cache-Control'] = 'public, max-age=3600'
        
        return response
    
    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/finance_tracker.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Finance Tracker startup')
        
    app.jinja_env.globals.update(
        get_category_color=get_category_color,
        get_category_icon =  get_category_icon
    )
    
    return app