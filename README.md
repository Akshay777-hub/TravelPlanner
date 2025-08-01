# AI Travel Planner

An AI-powered full-stack web application that helps users plan personalized travel itineraries based on preferences like destination, duration, interests, and budget. The app intelligently integrates geolocation, weather forecasting, flight/train options, and LLM-generated day-wise plans — all delivered via an interactive API-first design.

---

## Features

- User Authentication – Register and login securely using Supabase Auth.
- Personalized Itineraries – Generate daily plans tailored to the user's interests, destination, budget, and duration.
- Intelligent APIs:
  - Weather data from Open-Meteo
  - Real-time flights using Amadeus API
  - Simulated train options
  - Location geocoding via OpenStreetMap (Geopy)
  - AI-generated itineraries using Gemini API
- Interactive frontend served via Flask (can be swapped with React or others).
- API-first approach, ready to connect with any frontend.

---

## Tech Stack

| Layer       | Technologies Used                            |
|-------------|----------------------------------------------|
| Backend     | Flask (Python)                               |
| AI Engine   | Gemini API (Google)                          |
| Database    | Supabase (PostgreSQL)                        |
| APIs Used   | Open-Meteo, Amadeus, Geopy                   |
| Auth        | Supabase JWT                                 |
| Docs        | Swagger UI                                   |

---

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-travel-planner.git
cd ai-travel-planner
```

### 2. Create `.env` File

Add your API keys and Supabase credentials in a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret
```

---

## Running the Application

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask server:

```bash
python app.py
```

The app will run at `http://localhost:5000`

### API Docs

Visit: `http://localhost:5000/api/docs`  
(YAML spec: `http://localhost:5000/swagger.yaml`)

---

## API Endpoints Overview

### Authentication

- `POST /api/v1/auth/register` – Register a new user
- `POST /api/v1/auth/login` – Login and receive JWT

### Trip Management

- `POST /api/v1/trips` – Create a new trip plan
- `GET /api/v1/trips` – Fetch all user trips
- `GET /api/v1/trips/<trip_id>` – Get a specific trip
- `DELETE /api/v1/trips/<trip_id>` – Delete a trip

### Transportation (Standalone)

- `GET /api/v1/transport/flights?origin=...&destination=...&date=...`
- `GET /api/v1/transport/trains?origin=...&destination=...&date=...`

---

## Project Structure

```
.
├── __pycache__/           # Compiled Python files
├── frontend/              # Static frontend files (HTML, JS, CSS)
├── .cache.sqlite          # Cached API responses (Open-Meteo)
├── .env                   # Environment variables (not checked in)
├── app.py                 # Main application entry point
├── config.py              # API clients and config loading
├── routes.py              # API route definitions (Auth, Trips, Transport)
├── services.py            # Core logic (AI, transport, weather)
├── swagger.yaml           # OpenAPI specification for Swagger UI
```

---

## Built For

People10 Hackathon 2025  
Team: Innovatrix

---

