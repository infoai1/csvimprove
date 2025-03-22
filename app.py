import streamlit as st
import pandas as pd
import json
import requests

st.set_page_config(page_title="Quran Tafsir Enricher", layout="wide")
st.title("🕌 Quran Commentary Enrichment App")

uploaded_file = st.file_uploader("📂 Upload your Tafsir CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File loaded successfully!")
    st.dataframe(df.head())

    api_url = st.text_input("🔗 Paste your API Endpoint (Claude, DeepSeek, OpenAI, etc.)")
    api_key = st.text_input("🔑 API Key (leave blank if not needed)", type="password")

    if st.button("🚀 Enrich My Tafsir") and api_url:
        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Add empty columns for enrichment
        for col in ["themes", "wisdom_points", "real_life_reflections", "revelation_context"]:
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

Return result as JSON.
"""

          # Inside your enrichment loop
payload = {
    "model": "deepseek-chat",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "temperature": 0.4,
    "max_tokens": 800
}

response = requests.post(api_url, json=payload, headers=headers, timeout=30)
response_text = response.text
st.text(f"Row {idx + 1} response:")
st.code(response_text)

# Parse content
try:
    content = response.json()["choices"][0]["message"]["content"]
    result_data = json.loads(content)
except Exception as e:
    st.warning(f"Could not parse response for row {idx + 1}: {e}")
    result_data = {}

# Fill columns
for col in ["themes", "wisdom_points", "real_life_reflections", "revelation_context"]:
    df.at[idx, col] = result_data.get(col, "")

            except Exception as e:
                st.warning(f"⚠️ Row {idx + 1} failed: {e}")

        st.success("✅ Done enriching! Download below 👇")

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Enriched CSV", csv_data, file_name="enriched_tafsir.csv", mime="text/csv")
