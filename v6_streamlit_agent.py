import streamlit as st
import uuid
import os
import requests
import pdfkit
import folium
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from geopy.geocoders import Nominatim
import google.generativeai as genai

# --- Setup ---
st.set_page_config(page_title="✈️HJ Smart Travel Assistant", layout="wide")
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AVIATIONSTACK_KEY = os.getenv("AVIATIONSTACK_KEY", "5f427bc4eecf7a9f410f65bcfda6ab62")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

class UserContext(BaseModel):
    user_id: str
    preferred_airlines: list = Field(default_factory=list)
    hotel_amenities: list = Field(default_factory=list)
    budget_level: str = "mid-range"

# --- Session State ---
for k, v in {
    "chat_history": [],
    "user_context": UserContext(user_id=str(uuid.uuid4())),
    "language": "English"
}.items():
    if k not in st.session_state: st.session_state[k] = v

# --- Language Selector ---
lang_choice = st.sidebar.selectbox("🌐 Language", ["English", "اردو", "العربية"], index=["English", "اردو", "العربية"].index(st.session_state.language))
if lang_choice != st.session_state.language:
    st.session_state.language = lang_choice
    st.rerun()

lang = {
    "English": {
        "weather": "🌤️ Current Weather", "from": "From", "to": "To", "status": "Status",
        "not_found": "📍 Location not found.", "download": "📥 Download PDF", "reset": "🔁 Reset Planner",
        "export": "📄 Export as PDF", "assistant": "Assistant", "user": "You", "ask": "Ask anything about your trip 🌍"
    },
    "اردو": {
        "weather": "🌤️ موسم کی صورتحال", "from": "سے", "to": "تک", "status": "حالت",
        "not_found": "📍 مقام نہیں ملا۔", "download": "📥 پی ڈی ایف ڈاؤن لوڈ کریں", "reset": "🔁 منصوبہ دوبارہ شروع کریں",
        "export": "📄 چیٹ ایکسپورٹ کریں", "assistant": "مددگار", "user": "آپ", "ask": "سفر سے متعلق کوئی بھی سوال کریں 🌍"
    },
    "العربية": {
        "weather": "🌤️ الطقس الحالي", "from": "من", "to": "إلى", "status": "الحالة",
        "not_found": "📍 لم يتم العثور على الموقع.", "download": "📥 تحميل PDF", "reset": "🔁 إعادة تعيين الخطة",
        "export": "📄 تصدير الدردشة", "assistant": "المساعد", "user": "أنت", "ask": "اسأل أي شيء عن رحلتك 🌍"
    }
}[st.session_state.language]

# --- Custom Styling ---
st.markdown("""
<style>
.chat-box { padding:1rem; border-radius:12px; margin-bottom:1rem; background-color:#fff;
border-left:4px solid #4caf50; box-shadow:0 4px 10px rgba(0,0,0,0.1); word-break:break-word; }
.chat-user { border-color:#2196f3; background-color:#f0f8ff; }
.chat-ai { border-color:#4caf50; background-color:#f7f7f7; }
</style>
""", unsafe_allow_html=True)

# --- Location Input ---
st.sidebar.subheader("📍 Location")
try:
    city = requests.get("http://ip-api.com/json/").json().get("city", "Paris")
except:
    city = "Paris"

destination = st.sidebar.text_input("Enter City", value=city)
flight = st.sidebar.text_input("✈️ Flight IATA (e.g., EK202)")

st.title("🌐HJ Smart Travel Assistant")

geo = Nominatim(user_agent="travel-app")
loc = geo.geocode(destination)

if loc:
    c1, c2 = st.columns(2)
    with c1:
        m = folium.Map(location=[loc.latitude, loc.longitude], zoom_start=10)
        folium.Marker([loc.latitude, loc.longitude], popup=destination).add_to(m)
        st.components.v1.html(m._repr_html_(), height=300)

    with c2:
        st.subheader(lang["weather"])
        try:
            r = requests.get(f"https://wttr.in/{destination.replace(' ', '+')}?format=j1").json()["current_condition"][0]
            st.markdown(f"""
            **Temperature**: {r['temp_C']}°C  
            **Feels Like**: {r['FeelsLikeC']}°C  
            **Condition**: {r['weatherDesc'][0]['value']}  
            **Humidity**: {r['humidity']}%  
            **Wind**: {r['windspeedKmph']} km/h
            """)
        except:
            st.error("⚠️ Weather unavailable.")
else:
    st.warning(lang["not_found"])

# --- Flight Info ---
if flight:
    st.subheader(f"📡 Flight Info: {flight.upper()}")
    try:
        res = requests.get(f"http://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_KEY}&flight_iata={flight}").json()
        if res.get("data"):
            f = res["data"][0]
            st.markdown(f"""
            **Airline**: {f['airline']['name']}  
            **{lang['from']}**: {f['departure']['airport']}  
            **{lang['to']}**: {f['arrival']['airport']}  
            **Departure**: {f['departure']['scheduled']}  
            **Arrival**: {f['arrival']['scheduled']}  
            **{lang['status']}**: {f['flight_status'].capitalize()}
            """)
        else:
            st.warning("❌ Flight not found.")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# --- Chat ---
inp = st.chat_input(lang["ask"])
if inp:
    st.session_state.chat_history.append({"role": "user", "content": inp, "timestamp": datetime.now().strftime("%I:%M %p")})
    with st.spinner("💡 Gemini thinking..."):
        try:
            msgs = [{"role": "user", "parts": m["content"]} for m in st.session_state.chat_history if m["role"] == "user"]
            reply = model.generate_content(msgs).text
        except Exception as e:
            reply = f"❌ Error: {e}"
        st.session_state.chat_history.append({"role": "assistant", "content": reply, "timestamp": datetime.now().strftime("%I:%M %p")})
        st.rerun()

for m in st.session_state.chat_history:
    role = lang["user"] if m["role"] == "user" else lang["assistant"]
    css = "chat-user" if m["role"] == "user" else "chat-ai"
    st.markdown(f"<div class='chat-box {css}'><b>{role}</b>: {m['content']}<br><div style='opacity:0.6;font-size:12px'>{m['timestamp']}</div></div>", unsafe_allow_html=True)

# --- PDF Export ---
if st.sidebar.button(lang["export"]):
    html_content = "<h1>Travel Chat</h1><ul>" + "".join([f"<li><b>{lang['user'] if m['role']=='user' else lang['assistant']}</b>: {m['content']} ({m['timestamp']})</li>" for m in st.session_state.chat_history]) + "</ul>"
    with open("chat.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    pdfkit.from_file("chat.html", "chat.pdf")
    with open("chat.pdf", "rb") as f:
        st.download_button(lang["download"], data=f, file_name="chat.pdf", mime="application/pdf")

# --- Reset ---
if st.sidebar.button(lang["reset"]):
    st.session_state.chat_history = []
    st.success("✅ Reset done!")

# --- Footer ---
st.markdown("<hr style='margin-top:2rem;'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;font-size:13px;'>🌐 Smart Assistant · BUILD BY HAMMAD AHMAD· {st.session_state.language} · © 2025</div>", unsafe_allow_html=True)

