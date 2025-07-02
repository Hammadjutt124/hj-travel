import asyncio
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai
import os

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# --- Models for structured outputs ---

class TravelPlan(BaseModel):
    destination: str
    duration_days: int
    budget: float
    activities: List[str] = Field(description="List of recommended activities")
    notes: str = Field(description="Additional notes or recommendations")

# --- Function to generate travel plan from Gemini ---

async def generate_travel_plan(query: str) -> TravelPlan:
    system_prompt = """
You are a comprehensive travel planning assistant that helps users plan their perfect trip.

Always be helpful, informative, and enthusiastic about travel. Provide specific recommendations
based on the user's interests and preferences, budget, and travel duration.

Respond in the following JSON format:
{
  "destination": "...",
  "duration_days": ...,
  "budget": ...,
  "activities": ["...", "..."],
  "notes": "..."
}
"""

    # Use the Gemini model
    model = genai.GenerativeModel("gemini-pro")

    response = model.generate_content([
        {"role": "system", "parts": [system_prompt]},
        {"role": "user", "parts": [query]}
    ])

    try:
        content = response.text.strip()
        json_start = content.find('{')
        json_data = content[json_start:]
        travel_plan = TravelPlan.parse_raw(json_data)
        return travel_plan
    except Exception as e:
        raise RuntimeError(f"Failed to parse Gemini response:\n{response.text}\n\nError: {e}")

# --- Main Function ---

async def main():
    queries = [
        "I'm planning a trip to Miami for 5 days with a budget of $2000. What should I do there?",
        "I want to visit Tokyo for a week with a budget of $3000. What activities do you recommend?"
    ]

    for query in queries:
        print("\n" + "="*50)
        print(f"QUERY: {query}")

        try:
            travel_plan = await generate_travel_plan(query)

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

# import asyncio
# from typing import List
# from pydantic import BaseModel, Field
# from agents import Agent, Runner
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()

# model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')

# # --- Models for structured outputs ---

# class TravelPlan(BaseModel):
#     destination: str
#     duration_days: int
#     budget: float
#     activities: List[str] = Field(description="List of recommended activities")
#     notes: str = Field(description="Additional notes or recommendations")

# # --- Main Travel Agent ---

# travel_agent = Agent(
#     name="Travel Planner",
#     instructions="""
#     You are a comprehensive travel planning assistant that helps users plan their perfect trip.
    
#     You can create personalized travel itineraries based on the user's interests and preferences.
    
#     Always be helpful, informative, and enthusiastic about travel. Provide specific recommendations
#     based on the user's interests and preferences.
    
#     When creating travel plans, consider:
#     - Local attractions and activities
#     - Budget constraints
#     - Travel duration
#     """,
#     model=model,
#     output_type=TravelPlan
# )

# # --- Main Function ---

# async def main():
#     # Example queries to test the system
#     queries = [
#         "I'm planning a trip to Miami for 5 days with a budget of $2000. What should I do there?",
#         "I want to visit Tokyo for a week with a budget of $3000. What activities do you recommend?"
#     ]
    
#     for query in queries:
#         print("\n" + "="*50)
#         print(f"QUERY: {query}")
        
#         result = await Runner.run(travel_agent, query)
        
#         print("\nFINAL RESPONSE:")
#         travel_plan = result.final_output
        
#         # Format the output in a nicer way
#         print(f"\n🌍 TRAVEL PLAN FOR {travel_plan.destination.upper()} 🌍")
#         print(f"Duration: {travel_plan.duration_days} days")
#         print(f"Budget: ${travel_plan.budget}")
        
#         print("\n🎯 RECOMMENDED ACTIVITIES:")
#         for i, activity in enumerate(travel_plan.activities, 1):
#             print(f"  {i}. {activity}")
        
#         print(f"\n📝 NOTES: {travel_plan.notes}")

# if __name__ == "__main__":
#     asyncio.run(main())

