# streamlit_app.py

import streamlit as st
import pandas as pd
import json
import requests

st.set_page_config(page_title="Quran Tafsir Enricher", layout="wide")
st.title("🕌 Quran Commentary Enrichment App")

# Step 1: Upload CSV
uploaded_file = st.file_uploader("📂 Upload Tafsir CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File loaded successfully!")

    st.write("🔍 Preview of uploaded data:")
    st.dataframe(df.head())

    # Step 2: API Config
    st.subheader("🔗 API Configuration")
    api_url = st.text_input("API Endpoint (Claude, DeepSeek, OpenAI-compatible)")
    api_key = st.text_input("API Key (optional if your API doesn’t require it)", type="password")
    headers_input = st.text_area("Extra Headers (in JSON format, optional)", height=100)

    # Optional headers parsing
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    if headers_input.strip():
        try:
            extra_headers = json.loads(headers_input)
            headers.update(extra_headers)
        except Exception:
            st.warning("⚠️ Invalid JSON in headers input.")

    process_button = st.button("🚀 Enrich Tafsir")

    if process_button and api_url:
        st.info("🔄 Processing rows...")

        new_fields = ["themes", "wisdom_points", "real_life_reflections", "revelation_context"]
        for field in new_fields:
            df[field] = ""  # Create empty columns

        for idx, row in df.iterrows():
            commentary = str(row.get("English Commentary", ""))
            verse = str(row.get("Verse Text (Arabic)", ""))
            translation = str(row.get("Latest (English) Translation", ""))

            prompt = f"""
Given the Quranic verse: "{verse}" (Translation: "{translation}") and the following commentary: "{commentary}", extract the following:

1. Themes (1-3 keywords)
2. Wisdom points (short, deep insights)
3. Real-life reflections (modern, daily application)
4. Revelation context (if any)

Return your response in valid JSON format with fields:
- themes
- wisdom_points
- real_life_reflections
- revelation_context
"""

            payload = {
                "prompt": prompt,
                "temperature": 0.4,
                "max_tokens": 500
            }

            try:
                response = requests.post(api_url, json=payload, headers=headers, timeout=30)
                result = response.json()

                # Parse either directly as JSON or from string content
                if isinstance(result, dict):
                    result_data = result
                else:
                    result_data = json.loads(result)

                for field in new_fields:
                    df.at[idx, field] = result_data.get(field, "")

            except Exception as e:
                st.warning(f"⚠️ Error processing row {idx + 1}: {str(e)}")

        st.success("✅ Enrichment complete!")
        st.dataframe(df.head())

        # Download Enriched CSV
        csv_download = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Enriched CSV",
            data=csv_download,
            file_name="enriched_tafsir.csv",
            mime="text/csv"
        )
