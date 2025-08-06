import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Environment detection
    IS_PRODUCTION = os.environ.get('VERCEL') is not None
    
    # API settings
    LOGO_DEV_API_KEY = os.environ.get('LOGO_DEV_API_KEY') or 'pk_X1RlL8nWQ8ykU9TvaXQYBQ'
    
    # Cache settings
    CACHE_TYPE = 'simple' if not IS_PRODUCTION else 'null'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class VercelConfig(ProductionConfig):
    @staticmethod
    def init_app(app):
        ProductionConfig.init_app(app)
        
        # Force HTTPS in production
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'vercel': VercelConfig,
    'default': DevelopmentConfig
}