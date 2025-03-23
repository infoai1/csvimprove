import streamlit as st
import requests
from improvement1 import run_improvement1
from improvement2 import run_improvement2

st.set_page_config(page_title="Quran Tafsir Enricher", layout="wide")
st.title("🕌 Quran Commentary Enrichment App")

# Upload prompt
st.markdown("This app enriches Quranic commentary in two steps: first with core themes and reflections, then with deeper outlines and contextual questions.")

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

# API key input (once)
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
st.header("🧩 Improvement 1: Themes, Wisdom & Reflections")
run_improvement1(model_name, api_url, api_key, headers)

# -----------------------------
# STEP 2: Improvement 2 - Outlines & Contextual Questions
# -----------------------------
st.markdown("---")
st.header("📘 Improvement 2: Outline & Contextual Questions")
run_improvement2(model_name, api_url, api_key, headers)
