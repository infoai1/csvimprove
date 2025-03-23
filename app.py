import streamlit as st
import requests
from improvement1 import run_improvement1
from improvement2 import run_improvement2
from improvement3 import run_improvement3

st.set_page_config(page_title="Quran Tafsir Enricher", layout="wide")

# Centered layout using container
with st.container():
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.title("🕌 Quran Commentary Enrichment App")
    st.markdown("<p style='font-size: 18px;'>This app enriches Quranic commentary in three clear steps: first by extracting core themes and reflections (Improvement 1), then generating outlines and contextual questions (Improvement 2), and finally segmenting tafsir into thematic sections (Improvement 3).</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Centered controls layout
st.markdown("<div style='max-width: 800px; margin: auto;'>", unsafe_allow_html=True)

# Model selection
tabs = ["DeepSeek Reasoner", "Claude 3.5 Sonnet (via OpenRouter)", "Custom"]
model_choice = st.selectbox("🤖 Choose AI Model", tabs)

# Pre-fill model + endpoint
if model_choice == "DeepSeek Reasoner":
    api_url = "https://api.deepseek.com/v1/chat/completions"
    model_name = "deepseek-reasoner"
elif model_choice == "Claude 3.5 Sonnet (via OpenRouter)":
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    model_name = "anthropic/claude-3-sonnet"
else:
    api_url = st.text_input("🔗 Custom API Endpoint")
    model_name = st.text_input("💬 Custom Model Name")

# API key input
api_key = st.text_input("🔑 API Key", type="password")

# Shared headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# -----------------------------
# STEP 1: Improvement 1 - Core Enrichment
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>🧩 Improvement 1</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 16px;'>Extract core themes, wisdom points, real-life reflections, and revelation context from grouped tafsir commentary.</p>", unsafe_allow_html=True)
run_improvement1(model_name, api_url, api_key, headers)

# -----------------------------
# STEP 2: Improvement 2 - Outlines & Contextual Questions
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>📘 Improvement 2</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 16px;'>Generate a structured outline and insightful contextual questions to deepen understanding of each tafsir block.</p>", unsafe_allow_html=True)
run_improvement2(model_name, api_url, api_key, headers)

# -----------------------------
# STEP 3: Improvement 3 - Thematic Splitting
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>🧠 Improvement 3</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 16px;'>Split long tafsir blocks into smaller thematic sections (150–200 words), each with its own title, summary, keywords, and outline.</p>", unsafe_allow_html=True)
run_improvement3(model_name, api_url, api_key, headers)

# Close centered controls container
st.markdown("</div>", unsafe_allow_html=True)
