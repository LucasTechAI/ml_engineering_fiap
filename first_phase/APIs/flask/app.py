import logging
from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from settings.config import Config

from models.models import db
from routes.user_routes import register_user_routes
from routes.recipe_routes import recipe_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(
        level=logging.INFO,  
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting Flask application...")

    db.init_app(app)

    JWTManager(app)
    Swagger(app)

    register_user_routes(app)
    app.register_blueprint(recipe_bp)

    logger.info("Flask application setup complete.")
    return app


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created.")
    app.run(debug=True, port=5000)
