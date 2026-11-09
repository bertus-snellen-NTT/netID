"""
netID Flask Application
A UI for researching IP addresses, MAC addresses, and BGP ASes
"""

from flask import Flask

def create_app():
    """Application factory for creating the Flask app."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'netid-secret-key-change-in-production'
    
    # Import and register blueprints
    from app.routes.main_routes import main_routes
    from app.routes.ip_routes import ip_routes
    from app.routes.mac_routes import mac_routes
    from app.routes.bgp_routes import bgp_routes
    
    app.register_blueprint(main_routes)
    app.register_blueprint(ip_routes, url_prefix='/ip')
    app.register_blueprint(mac_routes, url_prefix='/mac')
    app.register_blueprint(bgp_routes, url_prefix='/bgp')
    
    return app
