# services.py
import json
import requests
from datetime import datetime
from config import geocode_ratelimited, openmeteo, amadeus, GEMINI_API_KEY

def get_weather_forecast(lat, lon, start_date, end_date):
    """Fetches weather forecast for the given location and duration."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
        "timezone": "auto", "start_date": start_date, "end_date": end_date
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temp_max = daily.Variables(1).ValuesAsNumpy()
    daily_temp_min = daily.Variables(2).ValuesAsNumpy()
    time_points = range(daily.Time(), daily.TimeEnd(), daily.Interval())

    forecast = []
    for i, time in enumerate(time_points):
        forecast.append({
            "date": datetime.fromtimestamp(time).strftime("%Y-%m-%d"),
            "weather_code": int(daily_weather_code[i]),
            "temp_max": float(round(daily_temp_max[i], 1)),
            "temp_min": float(round(daily_temp_min[i], 1))
        })
    return forecast

def get_flight_options(origin_city, destination_city, travel_date):
    """Fetches real-time flight options from Amadeus."""
    if not amadeus:
        return {"error": "Amadeus API client not configured."}
    try:
        origin_airports = amadeus.reference_data.locations.get(keyword=origin_city, subType='CITY,AIRPORT').data
        if not origin_airports: return {"error": f"Could not find airport code for {origin_city}"}
        origin_iata = origin_airports[0]['iataCode']

        dest_airports = amadeus.reference_data.locations.get(keyword=destination_city, subType='CITY,AIRPORT').data
        if not dest_airports: return {"error": f"Could not find airport code for {destination_city}"}
        dest_iata = dest_airports[0]['iataCode']

        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_iata,
            destinationLocationCode=dest_iata,
            departureDate=travel_date,
            adults=1,
            max=5
        )
        return response.data
    except Exception as e:
        return {"error": f"Could not fetch flight data: {e}"}

def simulate_train_options(origin_city, destination_city, travel_date):
    """Generates simulated train options."""
    return [
        {"train_name": "Intercity Express", "train_number": "12056", "departure_time": "08:00", "arrival_time": "16:30", "duration": "8h 30m", "price": {"amount": "1500", "currency": "INR"}},
        {"train_name": "Shatabdi Express", "train_number": "12002", "departure_time": "14:15", "arrival_time": "21:00", "duration": "6h 45m", "price": {"amount": "2200", "currency": "INR"}}
    ]

def generate_itinerary_with_coords(destination, start_date, end_date, budget, interests):
    """Generates a weather-aware, geocoded travel itinerary."""
    main_location = geocode_ratelimited(destination)
    if not main_location:
        raise Exception(f"Could not find coordinates for destination: {destination}")

    weather_data = get_weather_forecast(main_location.latitude, main_location.longitude, start_date, end_date)
    weather_prompt_string = json.dumps(weather_data)
    
    duration = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1

    prompt = f"""
    Act as an expert travel agent. Create a detailed, day-by-day travel itinerary for a {duration}-day trip to {destination}, starting on {start_date}.
    The traveler's budget is between {budget.get('min', 'N/A')} and {budget.get('max', 'N/A')} {budget.get('currency', 'USD')}. Their interests are {', '.join(interests)}.
    Here is the weather forecast: {weather_prompt_string}. Use this to suggest weather-appropriate activities.
    **Crucially, for each activity, you must provide the name of a real, specific, and geocodable point of interest.**
    For each day, provide suggestions for 'morning', 'afternoon', and 'evening' in that specific order, each with a "name" and "description".
    Provide the output as a valid JSON array where each object represents a day.
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}', headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        raise Exception(f"Failed to generate itinerary from Gemini. Status: {response.status_code}, Response: {response.text}")

    response_text = response.json()['candidates'][0]['content']['parts'][0]['text']
    itinerary = json.loads(response_text.strip().replace('```json', '').replace('```', ''))

    for i, day_plan in enumerate(itinerary):
        if i < len(weather_data): day_plan['weather'] = weather_data[i]
        for period in ['morning', 'afternoon', 'evening']:
            if period in day_plan and day_plan[period] and 'name' in day_plan[period]:
                location_name = day_plan[period]['name']
                try:
                    location = geocode_ratelimited(f"{location_name}, {destination}")
                    if location: day_plan[period]['location'] = {'name': location_name, 'lat': location.latitude, 'lng': location.longitude}
                    else: day_plan[period]['location'] = None
                except Exception as e:
                    print(f"Could not geocode {location_name}: {e}")
                    day_plan[period]['location'] = None
    return itinerary
