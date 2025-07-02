import asyncio
import os
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Models for structured outputs ---
class TravelPlan(BaseModel):
    destination: str
    duration_days: int
    budget: float
    activities: List[str] = Field(description="List of recommended activities")
    notes: str = Field(description="Additional notes or recommendations")

# --- Simulated weather tool ---
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
        conditions = weather_data[city]
        highest_prob = max(conditions, key=conditions.get)
        temp_range = {
            "New York": "15-25°C",
            "Los Angeles": "20-30°C",
            "Chicago": "10-20°C",
            "Miami": "25-35°C",
            "London": "10-18°C",
            "Paris": "12-22°C",
            "Tokyo": "15-25°C",
        }
        return f"The weather in {city} on {date} is forecasted to be {highest_prob} with temperatures around {temp_range.get(city, '15-25°C')}."
    else:
        return f"Weather forecast for {city} is not available."

# --- Generate travel plan using Gemini ---
async def generate_travel_plan(query: str, city: str, date: str) -> TravelPlan:
    weather_note = get_weather_forecast(city, date)

    system_prompt = f"""
You are a helpful AI travel planner.

Task: Create a personalized travel plan in JSON format. Consider:
- The user's travel query
- Destination weather forecast: {weather_note}
- Budget and trip duration
- Popular local attractions and activities

Respond only in the following JSON structure:
{{
  "destination": "...",
  "duration_days": ...,
  "budget": ...,
  "activities": ["...", "..."],
  "notes": "..."
}}

User query: {query}
"""

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(system_prompt)

    try:
        content = response.text.strip()
        json_start = content.find('{')
        travel_json = content[json_start:]
        travel_plan = TravelPlan.parse_raw(travel_json)
        return travel_plan
    except Exception as e:
        raise RuntimeError(f"Failed to parse Gemini response:\n{response.text}\n\nError: {e}")

# --- Main ---
async def main():
    queries = [
        ("I'm planning a trip to Miami for 5 days with a budget of $2000. What should I do there and what is the weather going to look like?", "Miami", "2025-08-10"),
        ("I want to visit Paris for a week with a budget of $3000. What activities do you recommend based on the weather?", "Paris", "2025-08-20")
    ]

    for query, city, date in queries:
        print("\n" + "="*50)
        print(f"QUERY: {query}")

        try:
            travel_plan = await generate_travel_plan(query, city, date)

            print("\nFINAL RESPONSE:")
            print(f"\n🌍 TRAVEL PLAN FOR {travel_plan.destination.upper()} 🌍")
            print(f"Duration: {travel_plan.duration_days} days")
            print(f"Budget: ${travel_plan.budget}")

            print("\n🎯 RECOMMENDED ACTIVITIES:")
            for i, activity in enumerate(travel_plan.activities, 1):
                print(f"  {i}. {activity}")

            print(f"\n📝 NOTES: {travel_plan.notes}")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
