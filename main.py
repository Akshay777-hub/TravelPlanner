# app.py
from flask import Flask, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from routes import api # Import the blueprint
import os

app = Flask(__name__)

# --- Swagger UI Configuration ---
SWAGGER_URL = '/api/docs'
API_URL = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "AI Travel Planner API"}
)
app.register_blueprint(swaggerui_blueprint)

# Register the API routes
app.register_blueprint(api)

# Route to serve the swagger.yaml file
@app.route('/swagger.yaml')
def send_swagger_yaml():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'swagger.yaml')

# Welcome route
@app.route('/')
def index():
    return jsonify({"msg": "Welcome to the AI Travel Planner API! Docs are at /api/docs"})

if __name__ == '__main__':
    app.run(debug=True)
