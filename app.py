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

    api_url = st.text_input("🔗 Enter Your API Endpoint (Claude, DeepSeek, etc.)")

    process_button = st.button("🚀 Enrich Tafsir")

    if process_button and api_url:
        st.info("Processing rows... This might take a while.")

        new_fields = ["themes", "wisdom_points", "real_life_reflections", "revelation_context"]
        for field in new_fields:
            df[field] = ""  # Empty columns to fill

        # Step 2: Loop through rows and enrich via API
        for idx, row in df.iterrows():
            commentary = row.get("English Commentary", "")
            verse = row.get("Verse Text (Arabic)", "")
            translation = row.get("Latest (English) Translation", "")

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

            # Use generic POST request – adapt to your specific API
            try:
                response = requests.post(api_url, json=payload)
                result_json = response.json()

                # Fill enriched fields
                for field in new_fields:
                    df.at[idx, field] = result_json.get(field, "")

            except Exception as e:
                st.warning(f"Error processing row {idx}: {str(e)}")

        # Step 3: Export enriched CSV
        st.success("🎉 Enrichment complete!")
        st.dataframe(df.head())

        @st.cache_data
        def convert_df(dataframe):
            return dataframe.to_csv(index=False).encode('utf-8')

        csv_download = convert_df(df)
        st.download_button(
            label="⬇️ Download Enriched CSV",
            data=csv_download,
            file_name='enriched_tafsir.csv',
            mime='text/csv'
        )
