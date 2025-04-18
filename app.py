import streamlit as st
import requests

from combined_enrichment import run_combined_enrichment
from improvement3 import run_improvement3
from improvement4 import run_improvement4
from improvement5 import run_improvement5
import config
import utils

# Page configuration
st.set_page_config(page_title="Quran Tafsir Enricher", layout="wide")

# Header section
with st.container():
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.title("🕌 Quran Commentary Enricher")
    st.markdown(
        """
        This tool enriches Quran commentary by:
        1. Combined Enrichment (Translations, Transliteration)
        2. Batch Refinement
        3. Thematic Splitting
        4. Embeddings & Relationship Mapping
        5. Chapter & Chunk Enrichment
        """, unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Load configuration\model_name = config.MODEL_NAME
embedding_model = config.EMBEDDING_MODEL
api_url = config.API_URL
embedding_api_url = config.EMBEDDING_API_URL
api_key = config.API_KEY
headers = {"Authorization": f"Bearer {api_key}"}

# -----------------------------
# Step 1: Combined Enrichment
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>✨ Step 1: Combined Enrichment</h2>", unsafe_allow_html=True)
run_combined_enrichment(model_name, api_url, headers)

# -----------------------------
# Step 2: Batch Refinement
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>⚙️ Step 2: Batch Refinement</h2>", unsafe_allow_html=True)
utils.batch_refinement(model_name, api_url, api_key, headers)

# -----------------------------
# Step 3: Thematic Splitting
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>🧠 Step 3: Thematic Splitting</h2>", unsafe_allow_html=True)
run_improvement3(model_name, api_url, api_key, headers)

# -----------------------------
# Step 4: Embeddings & Relationship Mapping
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>🔎 Step 4: Embeddings & Relationship Mapping</h2>", unsafe_allow_html=True)
run_improvement4(embedding_model, embedding_api_url, api_key, headers)

# -----------------------------
# Step 5: Chapter & Chunk Enrichment
# -----------------------------
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>📖 Step 5: Chapter & Chunk Enrichment</h2>", unsafe_allow_html=True)
run_improvement5(model_name, api_url, api_key, headers)
