# streamlit_app.py
import streamlit as st
import os
import google.generativeai as genai
from rag.vector_store import VectorStore
from logic.recommendation import recommend
from utils.validators import normalize_str, parse_npk_input, validate_choice
from utils.i18n import t, SUPPORTED_LANG

genai.configure(api_key="AIzaSyAjF4THQbVwSetjcnLkylwnPpqsvVgiZc0")
MODEL_NAME = "gemini-3-flash"

st.set_page_config(page_title="AgroSense", layout="wide")
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

if "lang" not in st.session_state:
    st.session_state.lang = "en"

lang = st.sidebar.selectbox("Language / भाषा:", ["English", "हिन्दी"], index=0)
st.session_state.lang = "hi" if lang.startswith("ह") else "en"

if "history" not in st.session_state:
    st.session_state.history = []

vs = VectorStore(json_path="rag/rag_chunks.json")

def get_validated_soil_info():
    try:
        soil_type = validate_choice(st.session_state.temp_soil_type, ["Sandy","Loamy","Clay","Red","Black","Kandi","Floodplain","Forest"])
        moisture = validate_choice(st.session_state.temp_moisture, ["Low","Medium","High"])
        organic = validate_choice(st.session_state.temp_organic, ["Poor","Average","Good"])
        n = parse_npk_input(st.session_state.temp_n)
        p = parse_npk_input(st.session_state.temp_p)
        k = parse_npk_input(st.session_state.temp_k)
        season = validate_choice(st.session_state.temp_season, ["Kharif","Rabi","Summer"])
        return soil_type, moisture, organic, n, p, k, season
    except ValueError as ve:
        st.error(t(st.session_state.lang, "error_invalid") + f" ({ve})")
        return None

def soil_info_form():
    st.session_state.temp_soil_type = st.text_input(t(st.session_state.lang, "soil_type"))
    st.session_state.temp_moisture  = st.text_input(t(st.session_state.lang, "moisture"))
    st.session_state.temp_organic   = st.text_input(t(st.session_state.lang, "organic"))
    st.session_state.temp_n = st.text_input(t(st.session_state.lang, "n_level"))
    st.session_state.temp_p = st.text_input(t(st.session_state.lang, "p_level"))
    st.session_state.temp_k = st.text_input(t(st.session_state.lang, "k_level"))
    st.session_state.temp_season = st.text_input(t(st.session_state.lang, "season"))
    if st.button("Submit"):
        validated = get_validated_soil_info()
        if validated:
            st.session_state.soil_info = validated
            st.session_state.soil_info_collected = True
            st.experimental_rerun()

def main():
    st.title("AgroSense 🌾 — Your Farming Assistant")

    for msg in st.session_state.history:
        if msg["sender"] == "user":
            st.markdown(f"**You:** {msg['text']}")
        else:
            st.markdown(f"**AgroSense:** {msg['text']}")

    user_input = st.chat_input("Type your question here...")

    if user_input:
        st.session_state.history.append({"sender":"user","text":user_input})
        st.session_state.soil_info_collected = False
        st.session_state.temp_soil_type = ""
        st.session_state.temp_moisture = ""
        st.session_state.temp_organic = ""
        st.session_state.temp_n = ""
        st.session_state.temp_p = ""
        st.session_state.temp_k = ""
        st.session_state.temp_season = ""
        st.session_state.history.append({"sender":"bot","text": t(st.session_state.lang, "ask_soil_info")})

    if st.session_state.get("soil_info_collected", False):
        soil_type, moisture, organic, n, p, k, season = st.session_state.soil_info
        query = f"{soil_type} soil, moisture {moisture}, organic {organic}, N={n[1]},P={p[1]},K={k[1]}, season {season}"
        chunks = vs.query(query, top_k=5, soil_filter=soil_type)
        rec = recommend(soil_type, moisture, organic, n, p, k, season, chunks)

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

        st.session_state.history.append({"sender":"bot","text":"\n".join(resp)})

    if not st.session_state.get("soil_info_collected", False) and len(st.session_state.history) == 0:
        st.session_state.history.append({"sender":"bot","text": t(st.session_state.lang, "greeting")})

if __name__ == "__main__":
    main()
