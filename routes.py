# routes.py
from flask import request, jsonify, Blueprint
from config import supabase
from services import (
    generate_itinerary_with_coords,
    get_flight_options,
    simulate_train_options
)

# Create a Blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

def get_user_from_token(request):
    """Helper function to get user from JWT token in request header."""
    token = request.headers.get('Authorization')
    if not token or len(token.split(" ")) < 2:
        return None, {"msg": "Missing or invalid Authorization header"}
    token = token.split(" ")[1]
    try:
        user = supabase.auth.get_user(token)
        return user, None
    except Exception as e:
        return None, {"msg": f"Invalid token: {e}"}

# --- Authentication Routes ---
@api.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        user_response = supabase.auth.sign_up({"email": data['email'], "password": data['password']})
        if user_response and user_response.user:
            supabase.table('profiles').insert({'id': user_response.user.id, 'email': user_response.user.email, 'preferences': data.get('preferences', {})}).execute()
        return jsonify({"msg": "User created successfully."}), 201
    except Exception as e:
        return jsonify({"msg": f"Could not register user: {e}"}), 400

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        session = supabase.auth.sign_in_with_password({"email": data['email'], "password": data['password']})
        return jsonify({"access_token": session.session.access_token, "user": {"id": session.user.id, "email": session.user.email}})
    except Exception as e:
        return jsonify({"msg": f"Bad email or password: {e}"}), 401

# --- Trip Routes ---
@api.route('/trips', methods=['POST'])
def create_trip():
    user, error = get_user_from_token(request)
    if error: return jsonify(error), 401
    data = request.get_json()
    if not all(k in data for k in ['destination', 'start_date', 'end_date', 'budget']):
        return jsonify({"msg": "Missing required fields"}), 400
    try:
        itinerary = generate_itinerary_with_coords(data['destination'], data['start_date'], data['end_date'], data.get('budget'), data.get('interests', []))
        trip_data = {'user_id': user.user.id, **data, 'itinerary': itinerary}
        response = supabase.table('trips').insert(trip_data).execute()
        return jsonify({"msg": "Trip created successfully", "trip": response.data[0]}), 201
    except Exception as e:
        return jsonify({"msg": f"Failed to create trip: {e}"}), 500

@api.route('/trips', methods=['GET'])
def get_trips():
    user, error = get_user_from_token(request)
    if error: return jsonify(error), 401
    response = supabase.table('trips').select("*").eq('user_id', user.user.id).execute()
    return jsonify(response.data)

@api.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    user, error = get_user_from_token(request)
    if error: return jsonify(error), 401
    response = supabase.table('trips').select("*").eq('id', trip_id).eq('user_id', user.user.id).execute()
    if not response.data: return jsonify({"msg": "Trip not found"}), 404
    return jsonify(response.data[0])

@api.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    user, error = get_user_from_token(request)
    if error: return jsonify(error), 401
    response = supabase.table('trips').delete().eq('id', trip_id).eq('user_id', user.user.id).execute()
    if not response.data: return jsonify({"msg": "Trip not found or not authorized"}), 404
    return jsonify({"msg": "Trip deleted successfully"})

# --- Transport Routes ---
@api.route('/trips/<int:trip_id>/transport/flights', methods=['GET'])
def get_flights_for_trip(trip_id):
    user, error = get_user_from_token(request)
    if error: return jsonify(error), 401
    origin = request.args.get('origin')
    if not origin: return jsonify({"msg": "Missing required query parameter: origin"}), 400
    trip_response = supabase.table('trips').select("destination, start_date").eq('id', trip_id).eq('user_id', user.user.id).execute()
    if not trip_response.data: return jsonify({"msg": "Trip not found"}), 404
    trip = trip_response.data[0]
    flight_options = get_flight_options(origin, trip['destination'], trip['start_date'])
    return jsonify(flight_options)

@api.route('/trips/<int:trip_id>/transport/trains', methods=['GET'])
def get_trains_for_trip(trip_id):
    user, error = get_user_from_token(request)
    if error: return jsonify(error), 401
    origin = request.args.get('origin')
    if not origin: return jsonify({"msg": "Missing required query parameter: origin"}), 400
    trip_response = supabase.table('trips').select("destination, start_date").eq('id', trip_id).eq('user_id', user.user.id).execute()
    if not trip_response.data: return jsonify({"msg": "Trip not found"}), 404
    trip = trip_response.data[0]
    train_options = simulate_train_options(origin, trip['destination'], trip['start_date'])
    return jsonify(train_options)
