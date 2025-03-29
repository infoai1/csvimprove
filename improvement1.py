import streamlit as st
import pandas as pd
import json
import requests

def run_improvement1(model_name, api_url, api_key, headers):
    st.header("🚀 Step 1: Enrich Tafsir by Commentary Group")
    uploaded_file = st.file_uploader("📂 Upload your Tafsir CSV", type="csv", key="step1")

    if uploaded_file and st.button("Run Step 1 Enrichment"):
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()
        st.success("✅ File loaded!")
        st.dataframe(df.head())
                # Debug: Show actual column names
        st.write("📊 Columns found:", df.columns.tolist())

        # Ensure required column exists
        if "Commentary Group" not in df.columns:
            st.error("❌ 'Commentary Group' column is missing from the uploaded file.")
            return

        # ✅ Safe to group now
        grouped = df.groupby("Commentary Group")

        for group_name, group_df in grouped:
            st.markdown(f"### ✨ Group: {group_name}")
            st.dataframe(group_df.head())

        enrich_fields = ["themes", "wisdom_points", "real_life_reflections", "revelation_context"]
        for field in enrich_fields:
            if field not in df.columns:
                df[field] = ""

        grouped = df.groupby("Commentary Group")
        group_results = {}

        for group_name, group_df in grouped:
            st.markdown(f"### 🧠 Processing Group: `{group_name}`")
            verse_text = " | ".join(group_df["Verse Text (Arabic)"].dropna().astype(str).tolist())
            translation = " | ".join(group_df["Latest (English) Translation"].dropna().astype(str).tolist())
            commentary_series = group_df["English Commentary"].dropna().astype(str)
            commentary = commentary_series.iloc[0] if not commentary_series.empty else "No commentary provided."

            prompt = f"""
Given the Quranic verses: \"{verse_text}\" 
(Translation: \"{translation}\") 
and this group commentary: \"{commentary}\", extract:

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
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
                "max_tokens": 800
            }

            try:
                with st.spinner(f"Processing group: {group_name}..."):
                    response = requests.post(api_url, headers=headers, json=payload, timeout=90)
                    raw_content = response.json()["choices"][0]["message"]["content"]
                    st.code(raw_content, language="json")

                    cleaned = raw_content.strip().replace("```json", "").replace("```", "").strip()
                    if not cleaned:
                        raise ValueError("Empty response from AI")

                    result_data = json.loads(cleaned)
                    group_results[group_name] = result_data

            except Exception as e:
                st.warning(f"⚠️ Failed to process group '{group_name}': {e}")
                group_results[group_name] = {key: "" for key in enrich_fields}

        for idx, row in df.iterrows():
            group_name = row["Commentary Group"]
            enriched = group_results.get(group_name, {})
            for field in enrich_fields:
                df.at[idx, field] = enriched.get(field, "")

        st.success("🎉 Step 1 Enrichment Complete!")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Enriched CSV (Step 1)", csv, file_name="enriched_step1.csv", mime="text/csv")
