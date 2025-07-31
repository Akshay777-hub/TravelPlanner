from flask import Flask, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from routes import api  # Import the blueprint
import os

app = Flask(__name__)
# Configure CORS to allow all origins for API routes
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/auth/*": {"origins": "*"}
})

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

# Route to serve the swagger.yaml file from the root directory
@app.route('/swagger.yaml')
def send_swagger_yaml():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'swagger.yaml')

# Serve static files from frontend directory
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('frontend', filename)

# Serve frontend.html as the index page
@app.route('/')
def index():
    return send_from_directory('frontend', 'frontend.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)