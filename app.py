from flask import Flask
from config import Config
from models import db # Import the db object from models.py
from routes import register_routes, login_manager # Import register_routes and login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config) # Load configuration from Config class

    db.init_app(app) # Initialize SQLAlchemy with the Flask app
    login_manager.init_app(app) # Initialize Flask-Login with the Flask app

    register_routes(app) # Register all your routes

    # You might need to create tables if they don't exist, though we did it via shell
    # with app.app_context():
    #     db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) # debug=True auto-reloads and shows detailed errors