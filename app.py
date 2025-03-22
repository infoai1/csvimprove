import streamlit as st
import pandas as pd
import json
import requests

st.set_page_config(page_title="Quran Tafsir Enricher", layout="wide")
st.title("🕌 Quran Commentary Enrichment App (Optimized by Group)")

# Step 1: Upload CSV
uploaded_file = st.file_uploader("📂 Upload your Tafsir CSV", type="csv")

# Step 2: Model dropdown
model_choice = st.selectbox(
    "🤖 Choose AI Model",
    ["DeepSeek Reasoner", "Claude 3.5 Sonnet (via OpenRouter)", "Custom"]
)


# Auto-fill API details
if model_choice == "DeepSeek Reasoner":
    api_url = "https://api.deepseek.com/v1/chat/completions"
    model_name = "deepseek-reasoner"
elif model_choice == "Claude 3.5 Sonnet (via OpenRouter)":
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    model_name = "anthropic/claude-3-sonnet"
else:
    api_url = st.text_input("🔗 Custom API Endpoint")
    model_name = st.text_input("💬 Custom Model Name")

# API Key input
api_key = st.text_input("🔑 API Key", type="password")

# Start enrichment
if uploaded_file and st.button("🚀 Enrich Tafsir by Commentary Group"):
    df = pd.read_csv(uploaded_file)
    st.success("✅ File loaded!")
    st.dataframe(df.head())

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    enrich_fields = ["themes", "wisdom_points", "real_life_reflections", "revelation_context"]
    for field in enrich_fields:
        if field not in df.columns:
            df[field] = ""

    # Extract unique groups
    grouped = df.groupby("Commentary Group")
    group_results = {}


    # Loop through the groups and process each group
    for group_name, group_df in grouped:
        st.markdown(f"### 🧠 Processing Group: `{group_name}`")
    
        verse_text = " | ".join(group_df["Verse Text (Arabic)"].dropna().astype(str).tolist())
        translation = " | ".join(group_df["Latest (English) Translation"].dropna().astype(str).tolist())
        
        # Handle empty commentary group
        commentary_series = group_df["English Commentary"].dropna().astype(str)
        commentary = commentary_series.iloc[0] if not commentary_series.empty else "No commentary provided."
    
        prompt = f"""
        Given the Quranic verses: "{verse_text}" 
        (Translation: "{translation}") 
        and this group commentary: "{commentary}", extract:
    
        - themes
        - wisdom_points
        - real_life_reflections
        - revelation_context
    
        Return result as **valid JSON** like this:
        {{
          "themes": [...],
          "wisdom_points": [...],
          "real_life_reflections": [...],
          "revelation_context": "..."
        }}
        """
        # Process the group with the AI API (as in the previous part)
        # ...

        
        prompt = f"""
Given the Quranic verses: "{verse_text}" 
(Translation: "{translation}") 
and this group commentary: "{commentary}", extract:

- themes
- wisdom_points
- real_life_reflections
- revelation_context

Return result as **valid JSON** like this:
{{
  "themes": [...],
  "wisdom_points": [...],
  "real_life_reflections": [...],
  "revelation_context": "..."
}}
"""

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
          with st.spinner(f"Processing group: {group_name}..."):
            response = requests.post(api_url, headers=headers, json=payload, timeout=90)
            raw_content = response.json()["choices"][0]["message"]["content"]
            st.code(raw_content, language="json")

            # Clean up markdown-style JSON blocks
            cleaned = raw_content.strip().replace("```json", "").replace("```", "").strip()

            if not cleaned:
                raise ValueError("Empty response from AI")

            result_data = json.loads(cleaned)
            group_results[group_name] = result_data

        except Exception as e:
            st.warning(f"⚠️ Failed to process group '{group_name}': {e}")
            group_results[group_name] = {key: "" for key in enrich_fields}

    # Apply results back to full DataFrame
    for idx, row in df.iterrows():
        group_name = row["Commentary Group"]
        enriched = group_results.get(group_name, {})
        for field in enrich_fields:
            df.at[idx, field] = enriched.get(field, "")

    st.success("🎉 Enrichment complete for all groups!")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Enriched CSV", csv, file_name="enriched_tafsir.csv", mime="text/csv")
