import streamlit as st
import requests
from combined_improvement import run_combined_improvement  # NEW combined module
from improvement4 import run_improvement4  # if you want to keep Improvement 4 separately
import config
import utils

st.set_page_config(page_title="Quran Tafsir Enricher", layout="wide")

# Intro Section (your existing code)
with st.container():
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.title("🕌 Quran Commentary Enricher")
    st.markdown(
        "<p style='font-size: 18px;'>"
        "This app enriches Quranic commentary in multiple steps. You can:"
        "<ul>"
        "<li>Extract core themes, reflections, and questions</li>"
        "<li>Split long tafsir into thematic sections</li>"
        "<li>Generate embeddings & relationship analysis</li>"
        "</ul>"
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='max-width: 800px; margin: auto;'>", unsafe_allow_html=True)

# Model & API Setup
model_choice = st.selectbox("🤖 Choose AI Chat Model", list(config.DEFAULT_CHAT_MODELS.keys()) + ["Custom"])
if model_choice != "Custom":
    chat_model = config.DEFAULT_CHAT_MODELS[model_choice]
    api_url = chat_model["api_url"]
    model_name = chat_model["model_name"]
else:
    api_url = st.text_input("🔗 Custom API Endpoint")
    model_name = st.text_input("💬 Custom Model Name")

embedding_choice = st.selectbox("🔎 Choose Embedding Model", list(config.EMBEDDING_MODELS.keys()))
embedding_model = config.EMBEDDING_MODELS[embedding_choice]
embedding_api_url = config.EMBEDDING_API_URL

api_key = st.text_input("🔑 API Key", type="password")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# -----------------------------
# Combined Enrichment & Thematic Splitting (Steps 1+3)
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>🧩 Combined Enrichment & Thematic Splitting</h2>", unsafe_allow_html=True)
run_combined_improvement(model_name, api_url, api_key, headers)

# Optionally, you can still have separate Improvement 4 for embeddings if desired:
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>🔎 Improvement 4: Embeddings & Relationship Mapping</h2>", unsafe_allow_html=True)
run_improvement4(embedding_model, embedding_api_url, api_key, headers)

st.markdown("</div>", unsafe_allow_html=True)
