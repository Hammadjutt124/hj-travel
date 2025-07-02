import os
import json
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.generativeai as genai

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ----- Models -----

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
    activities: List[str] = Field(description="List of recommended activities")
    notes: str = Field(description="Additional notes or recommendations")

class BudgetAnalysis(BaseModel):
    is_realistic: bool
    reasoning: str
    suggested_budget: Optional[float] = None

# ----- Tools -----

def get_weather_forecast(city: str, date: str) -> str:
    weather_data = {
        "Tokyo": {"sunny": 0.5, "rainy": 0.3, "cloudy": 0.2},
        "Paris": {"sunny": 0.4, "rainy": 0.3, "cloudy": 0.3}
    }
    if city in weather_data:
        forecast = max(weather_data[city], key=weather_data[city].get)
        return f"The weather in {city} on {date} is likely to be {forecast}."
    return f"Weather data for {city} is unavailable."

def search_flights(origin: str, destination: str, date: str) -> List[FlightRecommendation]:
    return [
        FlightRecommendation(
            airline="SkyWays",
            departure_time="08:00",
            arrival_time="10:30",
            price=350.00,
            direct_flight=True,
            recommendation_reason="Best balance of time and cost"
        ),
        FlightRecommendation(
            airline="OceanAir",
            departure_time="12:45",
            arrival_time="15:15",
            price=275.50,
            direct_flight=True,
            recommendation_reason="Cheapest option"
        )
    ]

def search_hotels(city: str, max_price: Optional[float] = None) -> List[HotelRecommendation]:
    hotels = [
        HotelRecommendation(
            name="City Center Hotel",
            location="Downtown",
            price_per_night=199.99,
            amenities=["WiFi", "Pool", "Gym"],
            recommendation_reason="Centrally located with modern amenities"
        ),
        HotelRecommendation(
            name="Riverside Inn",
            location="Riverside",
            price_per_night=149.50,
            amenities=["WiFi", "Free Breakfast"],
            recommendation_reason="Good value with breakfast included"
        )
    ]
    return [hotel for hotel in hotels if max_price is None or hotel.price_per_night <= max_price]

# ----- Gemini Prompt Logic -----

def build_travel_prompt(destination: str, days: int, budget: float) -> str:
    return (
        f"Plan a {days}-day trip to {destination} within a budget of ${budget}.\n"
        f"Include:\n"
        f"- A short list of recommended activities\n"
        f"- Notes or general suggestions\n"
        f"Respond in JSON using keys: destination, duration_days, budget, activities, notes"
    )

def generate_travel_plan(destination: str, days: int, budget: float) -> TravelPlan:
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = build_travel_prompt(destination, days, budget)
    response = model.generate_content(prompt)
    raw = response.text
    try:
        travel_json = raw[raw.find('{'):raw.rfind('}')+1]
        return TravelPlan(**json.loads(travel_json))
    except Exception as e:
        print("Parsing failed:", e)
        print("Raw response:\n", raw)
        raise

# ----- Budget Check -----

def analyze_budget(destination: str, days: int, budget: float) -> BudgetAnalysis:
    # Simulated check
    if budget < 500:
        return BudgetAnalysis(
            is_realistic=False,
            reasoning="This budget may not be enough for accommodation and flights.",
            suggested_budget=1000
        )
    return BudgetAnalysis(
        is_realistic=True,
        reasoning="The budget is realistic for a mid-range trip."
    )

# ----- Main Function -----

def main():
    destination = "Tokyo"
    days = 7
    budget = 300  # Try low to trigger budget warning

    print(f"\n🧭 Trip to {destination} for {days} days with ${budget} budget\n")

    budget_result = analyze_budget(destination, days, budget)
    if not budget_result.is_realistic:
        print(f"⚠️ Budget Warning: {budget_result.reasoning}")
        if budget_result.suggested_budget:
            print(f"Suggested budget: ${budget_result.suggested_budget}\n")

    print("🌤️ Weather Forecast:")
    print(get_weather_forecast(destination, datetime.now().strftime('%Y-%m-%d')))

    print("\n🛫 Available Flights:")
    for flight in search_flights("New York", destination, "2025-07-10"):
        print(f"- {flight.airline} | ${flight.price} | {flight.departure_time}–{flight.arrival_time} | {flight.recommendation_reason}")

    print("\n🏨 Hotel Options:")
    for hotel in search_hotels(destination, max_price=200):
        print(f"- {hotel.name} (${hotel.price_per_night}) | {', '.join(hotel.amenities)}")

    print("\n📝 Travel Plan:")
    plan = generate_travel_plan(destination, days, budget)
    print(f"\n🌍 Destination: {plan.destination}")
    print(f"🕒 Duration: {plan.duration_days} days")
    print(f"💰 Budget: ${plan.budget}")
    print("\n🎯 Activities:")
    for act in plan.activities:
        print(f"  - {act}")
    print(f"\n📌 Notes: {plan.notes}")

if __name__ == "__main__":
    main()
