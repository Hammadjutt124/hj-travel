


import streamlit as st
import uuid
import os
from datetime import datetime
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# Streamlit page settings
st.set_page_config(page_title="Gemini Travel Planner", layout="wide", page_icon="✈️")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Format Gemini output
def format_response(raw_text):
    try:
        output = json.loads(raw_text)
        if "destination" in output:
            return f"""**✈️ Travel Plan to {output['destination']}**
- Duration: {output['duration_days']} days  
- Budget: ${output['budget']}  
- Activities: {', '.join(output['activities'])}  
- Notes: {output['notes']}"""
        elif "airline" in output:
            return f"""**🛫 Flight Recommendation**  
Airline: {output['airline']}  
Departure: {output['departure_time']} → Arrival: {output['arrival_time']}  
Price: ${output['price']}  
Direct: {"Yes" if output['direct_flight'] else "No"}  
Reason: {output['recommendation_reason']}"""
        elif "name" in output and "amenities" in output:
            return f"""**🏨 Hotel Recommendation: {output['name']}**  
Location: {output['location']}  
Price per Night: ${output['price_per_night']}  
Amenities: {', '.join(output['amenities'])}  
Reason: {output['recommendation_reason']}"""
    except:
        return raw_text

# Display previous messages
st.title("🧳 HJ Travel Planner Assistant")
st.caption("Ask about flights, hotels, activities, budgets, or full travel plans.")

for msg in st.session_state.chat_history:
    role = "🧑‍💼" if msg["role"] == "user" else "🤖"
    st.markdown(f"**{role} {msg['timestamp']}**: {msg['content']}")

# Input
user_input = st.chat_input("Where would you like to travel?")
if user_input:
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })

    with st.spinner("Planning your adventure..."):
        try:
            response = model.generate_content(user_input)
            formatted_reply = format_response(response.text)
        except Exception as e:
            formatted_reply = f"⚠️ Error: {str(e)}"

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": formatted_reply,
        "timestamp": datetime.now().strftime("%I:%M %p")
    })
    st.rerun()

# Footer
st.divider()
st.caption("Powered by Hammad Ahmad | Built with openai sdk")
