# streamlit_app.py
import os
import streamlit as st
from rag.vector_store import VectorStore
from logic.recommendation import recommend
from utils.validators import normalize_str, parse_npk_input
from utils.i18n import t, SUPPORTED_LANG

# Configure API (if you later integrate LLM for more fluent responses)
# import google.generativeai as genai
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="AgroSense 🌾", layout="wide")

# CSS for "glass-morphism" look
st.markdown("""
<style>
.chat-container {
  backdrop-filter: blur(8px);
  background: rgba(255,255,255,0.25);
  border-radius: 12px;
  padding: 16px;
}
.user { color: #1a1a1a; }
.bot  { color: #0b3d0b; }
</style>
""", unsafe_allow_html=True)

# Language selector
if "lang" not in st.session_state:
    st.session_state.lang = "en"
lang = st.sidebar.selectbox("Language / भाषा:", ["English", "हिन्दी"], index=0)
st.session_state.lang = "hi" if lang.startswith("ह") else "en"

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []
# Flow control
if "step" not in st.session_state:
    st.session_state.step = 0  # 0 = greeting, 1 = ask soil info, 2 = soil-input stage, 3 = recommendation

@st.cache_resource
def load_vector_store():
    return VectorStore(json_path="rag/rag_chunks.json")
vs = load_vector_store()

def reset_flow():
    st.session_state.step = 1
    st.session_state.soil_info = {}

def add_user_message(msg):
    st.session_state.history.append({"sender": "user", "text": msg})

def add_bot_message(msg):
    st.session_state.history.append({"sender": "bot", "text": msg})

def render_chat_history():
    for msg in st.session_state.history:
        if msg["sender"] == "user":
            st.markdown(f"**You:** {msg['text']}")
        else:
            st.markdown(f"**AgroSense:** {msg['text']}")

def ask_soil_inputs():
    add_bot_message(t(st.session_state.lang, "ask_soil_info"))

    with st.form(key="soil_form"):
        soil_type = st.selectbox(
            t(st.session_state.lang, "soil_type"),
            ["Sandy","Loamy","Clay","Red","Black","Kandi","Floodplain","Forest","Other"]
        )
        if soil_type == "Other":
            soil_type = st.text_input("If other, type soil type:")

        moisture = st.selectbox(
            t(st.session_state.lang, "moisture"),
            ["Low","Medium","High","Other"]
        )
        if moisture == "Other":
            moisture = st.text_input("If other, type moisture level:")

        organic = st.selectbox(
            t(st.session_state.lang, "organic"),
            ["Poor","Average","Good","Other"]
        )
        if organic == "Other":
            organic = st.text_input("If other, type organic content level:")

        n_input = st.text_input(t(st.session_state.lang, "n_level"))
        p_input = st.text_input(t(st.session_state.lang, "p_level"))
        k_input = st.text_input(t(st.session_state.lang, "k_level"))

        season = st.selectbox(
            t(st.session_state.lang, "season"),
            ["Kharif","Rabi","Summer","Other"]
        )
        if season == "Other":
            season = st.text_input("If other, type season:")

        submitted = st.form_submit_button("Submit")

        if submitted:
            # Validate
            try:
                n = parse_npk_input(n_input)
                p = parse_npk_input(p_input)
                k = parse_npk_input(k_input)

                soil_type_norm = normalize_str(soil_type)
                moisture_norm  = normalize_str(moisture)
                organic_norm   = normalize_str(organic)
                season_norm    = normalize_str(season)

                st.session_state.soil_info = {
                    "soil_type": soil_type_norm,
                    "moisture": moisture_norm,
                    "organic": organic_norm,
                    "n": n,
                    "p": p,
                    "k": k,
                    "season": season_norm
                }
                st.session_state.step = 3
            except ValueError as e:
                st.error(f"{t(st.session_state.lang, 'error_invalid')} — {e}")

def generate_recommendation():
    sio = st.session_state.soil_info
    query = f"Soil: {sio['soil_type']}, moisture {sio['moisture']}, organic {sio['organic']}, N={sio['n'][1]},P={sio['p'][1]},K={sio['k'][1]}, season:{sio['season']}"
    chunks = vs.query(query, top_k=5, soil_filter=sio['soil_type'])
    rec = recommend(sio['soil_type'], sio['moisture'], sio['organic'],
                    sio['n'], sio['p'], sio['k'], sio['season'], chunks)

    resp = []
    resp.append("✅ *Suitable Crops:* " + ", ".join(rec["crops"]))
    resp.append("🌱 *Fertilizer / Soil Improvement:*")
    for f in rec["fertilizer"]:
        resp.append("- " + f)
    for s in rec["soil_improvement"]:
        resp.append("- " + s)
    resp.append("🧑‍🌾 *Care Tips:*")
    for c in rec["care_tips"]:
        resp.append("- " + c)

    add_bot_message("\n".join(resp))

def main():
    if st.session_state.step == 0:
        add_bot_message(t(st.session_state.lang, "greeting"))
        st.session_state.step = 1

    render_chat_history()

    if st.session_state.step == 1:
        if st.button("Start Farming Advice"):
            reset_flow()

    elif st.session_state.step == 1 and st.session_state.history and st.session_state.history[-1]["sender"] == "bot":
        ask_soil_inputs()

    elif st.session_state.step == 3:
        generate_recommendation()
        st.session_state.step = 0  # Reset for next session

if __name__ == "__main__":
    main()
