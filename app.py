import streamlit as st
import requests
from improvement1 import run_improvement1
from improvement2 import run_improvement2
from improvement3 import run_improvement3
from improvement4 import run_improvement4
import config
import utils

st.set_page_config(page_title="Quran Tafsir Enricher", layout="wide")

# Centered layout using container
with st.container():
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.title("🕌 Quran Commentary Enricher")
    st.markdown(
        "<p style='font-size: 18px;'>"
        "This app enriches Quranic commentary in multiple steps: "
        "Improvement 1 extracts core themes and reflections; Improvement 2 generates outlines and contextual questions; "
        "Improvement 3 splits tafsir into thematic sections; and Improvement 4 adds embeddings and relationship analysis."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Centered controls layout
st.markdown("<div style='max-width: 800px; margin: auto;'>", unsafe_allow_html=True)

# -----------------------------
# Chat Model Selection
# -----------------------------
model_choice = st.selectbox("🤖 Choose AI Chat Model", list(config.DEFAULT_CHAT_MODELS.keys()) + ["Custom"])
if model_choice != "Custom":
    chat_model = config.DEFAULT_CHAT_MODELS[model_choice]
    api_url = chat_model["api_url"]
    model_name = chat_model["model_name"]
else:
    api_url = st.text_input("🔗 Custom API Endpoint")
    model_name = st.text_input("💬 Custom Model Name")

# -----------------------------
# Embedding Model Selection
# -----------------------------
embedding_choice = st.selectbox("🔎 Choose OpenAI Embedding Model", list(config.EMBEDDING_MODELS.keys()))
embedding_model = config.EMBEDDING_MODELS[embedding_choice]
embedding_api_url = config.EMBEDDING_API_URL

# -----------------------------
# API Key Input
# -----------------------------
api_key = st.text_input("🔑 API Key", type="password")

# Shared headers for Chat API (and used for Embeddings as well)
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# -----------------------------
# STEP 1: Improvement 1 - Core Enrichment
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>🧩 Improvement 1</h2>", unsafe_allow_html=True)
run_improvement1(model_name, api_url, api_key, headers)

# -----------------------------
# STEP 2: Improvement 2 - Outlines & Contextual Questions
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>📘 Improvement 2</h2>", unsafe_allow_html=True)
run_improvement2(model_name, api_url, api_key, headers)

# -----------------------------
# STEP 3: Improvement 3 - Thematic Splitting
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>🧠 Improvement 3</h2>", unsafe_allow_html=True)
run_improvement3(model_name, api_url, api_key, headers)

# -----------------------------
# STEP 4: Improvement 4 - Embeddings & Relationship Analysis
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>🔎 Improvement 4</h2>", unsafe_allow_html=True)
run_improvement4(embedding_model, embedding_api_url, api_key, headers)

# Close centered container
st.markdown("</div>", unsafe_allow_html=True)
