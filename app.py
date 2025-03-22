import streamlit as st
import pandas as pd
import json
import requests

st.set_page_config(page_title="Quran Tafsir Enricher", layout="wide")
st.title("🕌 Quran Commentary Enrichment App")

uploaded_file = st.file_uploader("📂 Upload your Tafsir CSV", type="csv")

# =======================
# Step 1: Model Selector
# =======================
model_choice = st.selectbox(
    "🤖 Choose AI Model",
    ["DeepSeek Reasoner", "Claude 3.5 Sonnet (via OpenRouter)", "Custom"]
)

# Pre-fill endpoint and model name
if model_choice == "DeepSeek Reasoner":
    api_url = "https://api.deepseek.com/v1/chat/completions"
    model_name = "deepseek-chat"
elif model_choice == "Claude 3.5 Sonnet (via OpenRouter)":
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    model_name = "anthropic/claude-3-sonnet"
else:
    api_url = st.text_input("🔗 Custom API Endpoint")
    model_name = st.text_input("💬 Custom Model Name")

api_key = st.text_input("🔑 API Key", type="password")

# =======================
# Step 2: Enrichment
# =======================
if uploaded_file and st.button("🚀 Enrich Tafsir"):
    df = pd.read_csv(uploaded_file)
    st.success("✅ File loaded successfully!")
    st.dataframe(df.head())

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    enrich_fields = ["themes", "wisdom_points", "real_life_reflections", "revelation_context"]
    for col in enrich_fields:
        if col not in df.columns:
            df[col] = ""

    for idx, row in df.iterrows():
        verse = str(row.get("Verse Text (Arabic)", ""))
        translation = str(row.get("Latest (English) Translation", ""))
        commentary = str(row.get("English Commentary", ""))

        prompt = f"""
Given the Quranic verse: "{verse}" (Translation: "{translation}") and commentary: "{commentary}", extract:

- themes
- wisdom_points
- real_life_reflections
- revelation_context

Return result as valid JSON in this format:
{{
  "themes": [...],
  "wisdom_points": [...],
  "real_life_reflections": [...],
  "revelation_context": "..."
}}
"""

        # Payload for OpenAI/DeepSeek-compatible APIs
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4,
            "max_tokens": 800
        }



        try:
            content = response.json()["choices"][0]["message"]["content"]
            st.code(content, language="json")
        
            # Clean markdown-style code blocks
            
            cleaned = content.strip().replace("```json", "").replace("```", "").strip()

            if not cleaned:
                raise ValueError("Empty response from AI.")
            
            result_data = json.loads(cleaned)

            
        
        
            for col in enrich_fields:
                df.at[idx, col] = result_data.get(col, "")
        
        except Exception as e:
            st.warning(f"⚠️ Row {idx + 1} failed: {e}")


    st.success("✅ Enrichment completed!")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Enriched CSV", csv, file_name="enriched_tafsir.csv", mime="text/csv")
