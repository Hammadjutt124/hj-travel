import os
import json
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Make sure the key name is correct

# --- Models ---

class FlightRecommendation(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    price: float
    direct_flight: bool
    recommendation_reason: str

class HotelRecommendation(BaseModel):
    name: str
    location: str
    price_per_night: float
    amenities: List[str]
    recommendation_reason: str

class TravelPlan(BaseModel):
    destination: str
    duration_days: int
    budget: float
    activities: List[str]
    notes: str

# --- Simulated Tools ---

def get_weather_forecast(city: str, date: str) -> str:
    weather_data = {
        "New York": {"sunny": 0.3, "rainy": 0.4, "cloudy": 0.3},
        "Los Angeles": {"sunny": 0.8, "rainy": 0.1, "cloudy": 0.1},
        "Chicago": {"sunny": 0.4, "rainy": 0.3, "cloudy": 0.3},
        "Miami": {"sunny": 0.7, "rainy": 0.2, "cloudy": 0.1},
        "London": {"sunny": 0.2, "rainy": 0.5, "cloudy": 0.3},
        "Paris": {"sunny": 0.4, "rainy": 0.3, "cloudy": 0.3},
        "Tokyo": {"sunny": 0.5, "rainy": 0.3, "cloudy": 0.2},
    }
    if city in weather_data:
        highest = max(weather_data[city], key=weather_data[city].get)
        return f"{city} on {date} is expected to be {highest} with temperatures around 20–30°C."
    return f"Weather forecast for {city} on {date} is not available."

def search_flights(origin: str, destination: str, date: str) -> List[dict]:
    return [
        {
            "airline": "SkyWays",
            "departure_time": "08:00",
            "arrival_time": "10:30",
            "price": 350.00,
            "direct_flight": True,
            "recommendation_reason": "Best balance of time and price"
        },
        {
            "airline": "OceanAir",
            "departure_time": "12:45",
            "arrival_time": "15:15",
            "price": 275.50,
            "direct_flight": True,
            "recommendation_reason": "Cheapest direct flight"
        }
    ]

def search_hotels(city: str, max_price: Optional[float] = None) -> List[dict]:
    hotels = [
        {
            "name": "City Center Hotel",
            "location": "Downtown",
            "price_per_night": 199.99,
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
            "recommendation_reason": "Central location with all essentials"
        },
        {
            "name": "Riverside Inn",
            "location": "Riverside",
            "price_per_night": 149.50,
            "amenities": ["WiFi", "Free Breakfast", "Parking"],
            "recommendation_reason": "Affordable with breakfast included"
        },
        {
            "name": "Luxury Palace",
            "location": "Historic District",
            "price_per_night": 349.99,
            "amenities": ["WiFi", "Spa", "Fine Dining", "Concierge"],
            "recommendation_reason": "Premium comfort and services"
        }
    ]
    return [h for h in hotels if max_price is None or h["price_per_night"] <= max_price]

# --- Gemini Prompt Builder ---

def build_travel_prompt(destination: str, days: int, budget: float) -> str:
    return (
        f"Plan a {days}-day trip to {destination} within a budget of ${budget}.\n"
        f"Include:\n"
        f"1. List of activities\n"
        f"2. Travel notes\n"
        f"3. Best weather day forecast\n"
        f"Respond in JSON format using fields: destination, duration_days, budget, activities, notes."
    )

# --- Gemini Call & Parsing ---

def generate_travel_plan(destination: str, days: int, budget: float) -> TravelPlan:
    prompt = build_travel_prompt(destination, days, budget)
    model = genai.GenerativeModel("gemini-1.5-pro")  # Updated model name
    response = model.generate_content(prompt)

    try:
        raw = response.text
        json_start = raw.find('{')
        json_end = raw.rfind('}') + 1
        travel_json = raw[json_start:json_end]
        data = json.loads(travel_json)
        return TravelPlan(**data)
    except Exception as e:
        print("Failed to parse response:", e)
        print("Raw response:\n", response.text)
        raise

# --- Run Example ---

if __name__ == "__main__":
    destination = "Tokyo"
    days = 5
    budget = 2000

    print("📦 Getting travel plan...\n")
    plan = generate_travel_plan(destination, days, budget)

    print(f"\n🌍 Travel Plan for {plan.destination}")
    print(f"Duration: {plan.duration_days} days")
    print(f"Budget: ${plan.budget}")
    print("\n🎯 Activities:")
    for i, act in enumerate(plan.activities, 1):
        print(f"  {i}. {act}")
    print(f"\n📝 Notes: {plan.notes}")
