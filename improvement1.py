import streamlit as st
import pandas as pd
import json
import requests

def run_improvement1(model_name, api_url, api_key, headers):
    st.header("🚀 Step 1: Enrich Tafsir by Verse Group")
    uploaded_file = st.file_uploader("📂 Upload your Tafsir CSV", type="csv", key="step1")

    if uploaded_file and st.button("Run Step 1 Enrichment"):
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()  # Normalize column names

        st.success("✅ File loaded!")
        st.dataframe(df.head())
        st.write("📊 Columns found:", df.columns.tolist())

        # 🔐 Validate required columns based on this file
        required_columns = ["Verse Group", "English Commentary", "translation"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"❌ Missing required columns: {missing}")
            return

        # Create enrichment fields if not present
        enrich_fields = ["themes", "wisdom_points", "real_life_reflections", "revelation_context"]
        for field in enrich_fields:
            if field not in df.columns:
                df[field] = ""

        grouped = df.groupby("Verse Group")
        group_results = {}

        for group_name, group_df in grouped:
            st.markdown(f"### 🧠 Processing Group: `{group_name}`")

            translation = " | ".join(group_df["translation"].dropna().astype(str).tolist())
            commentary_series = group_df["English Commentary"].dropna().astype(str)
            commentary = commentary_series.iloc[0] if not commentary_series.empty else "No commentary provided."

            prompt = f"""
Given this English Quranic translation: \"{translation}\"  
And this group commentary: \"{commentary}\", extract:

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
                    content = response.json()["choices"][0]["message"]["content"]

                    cleaned = content.strip().replace("```json", "").replace("```", "").strip()
                    if not cleaned:
                        raise ValueError("Empty response from AI")

                    result_data = json.loads(cleaned)
                    st.code(json.dumps(result_data, indent=2), language="json")
                    group_results[group_name] = result_data

            except Exception as e:
                st.warning(f"⚠️ Failed to process group '{group_name}': {e}")
                group_results[group_name] = {key: "" for key in enrich_fields}

        # Apply enrichment results to DataFrame
        for idx, row in df.iterrows():
            enriched = group_results.get(row["Verse Group"], {})
            for field in enrich_fields:
                df.at[idx, field] = enriched.get(field, "")

        st.success("🎉 Step 1 Enrichment Complete!")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Enriched CSV (Step 1)", csv, file_name="enriched_step1.csv", mime="text/csv")
