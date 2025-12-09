"""
Main Flask application entry point.
This file initializes the Flask app and registers all blueprints.
"""
from flask import Flask
from flask_cors import CORS
from config import Config


def create_app(config_class=Config):
    """
    Application factory pattern.
    Creates and configures the Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for development (adjust for production)
    CORS(app)
    
    # Register blueprints
    from blueprints.main import main_bp
    from blueprints.api.game import game_bp
    from blueprints.api.combat import combat_bp
    from blueprints.api.travel import travel_bp
    from blueprints.api.inventory import inventory_bp
    from blueprints.api.story import story_bp
    from blueprints.api.audio import audio_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(game_bp, url_prefix='/api/game')
    app.register_blueprint(combat_bp, url_prefix='/api/combat')
    app.register_blueprint(travel_bp, url_prefix='/api/travel')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(story_bp, url_prefix='/api/story')
    app.register_blueprint(audio_bp, url_prefix='/api/audio')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

    
