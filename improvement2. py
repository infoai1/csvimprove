# improvement2.py

import streamlit as st
import pandas as pd
import json
import requests

def run_improvement2(model_name, api_url, api_key, headers):
    st.header("🔁 Improvement 2: Add Outline & Contextual Questions")
    improvement2_file = st.file_uploader("📂 Upload CSV from Improvement 1", type="csv", key="improvement2")

    if improvement2_file and st.button("🚀 Add Outline & Contextual Questions"):
        df2 = pd.read_csv(improvement2_file)
        st.success("✅ File loaded for improvement 2!")
        st.dataframe(df2.head())

        for field in ["outline_of_commentary", "contextual_questions"]:
            if field not in df2.columns:
                df2[field] = ""

        grouped2 = df2.groupby("Commentary Group")
        group_results_2 = {}

        for group_name, group_df in grouped2:
            st.markdown(f"🧠 Enriching Group: `{group_name}` with outline and questions")

            verse_text = " | ".join(group_df["Verse Text (Arabic)"].dropna().astype(str).tolist())
            translation = " | ".join(group_df["Latest (English) Translation"].dropna().astype(str).tolist())
            commentary_series = group_df["English Commentary"].dropna().astype(str)
            commentary = commentary_series.iloc[0] if not commentary_series.empty else "No commentary provided."

            prompt = f"""
Given the following Quranic verses: "{verse_text}"
(Translation: "{translation}")
and commentary: "{commentary}", generate:

1. An 'outline_of_commentary' – a clear bullet-point summary of key ideas.
2. 'contextual_questions' – 4–6 questions that explain and explore the deeper meaning in context. Each question should function as an explanation in disguise.

Return result as valid JSON in this format:
{{
  "outline_of_commentary": [...],
  "contextual_questions": [...]
}}
"""

            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
                "max_tokens": 800
            }

            try:
                response = requests.post(api_url, headers=headers, json=payload, timeout=90)
                raw_content = response.json()["choices"][0]["message"]["content"]
                cleaned = raw_content.strip().replace("```json", "").replace("```", "").strip()
                result_data = json.loads(cleaned)
                group_results_2[group_name] = result_data
            except Exception as e:
                st.warning(f"⚠️ Group {group_name} failed: {e}")
                group_results_2[group_name] = {
                    "outline_of_commentary": "",
                    "contextual_questions": ""
                }

        for idx, row in df2.iterrows():
            group_name = row["Commentary Group"]
            enriched = group_results_2.get(group_name, {})
            df2.at[idx, "outline_of_commentary"] = enriched.get("outline_of_commentary", "")
            df2.at[idx, "contextual_questions"] = enriched.get("contextual_questions", "")

        st.success("🎉 Outline & Questions added!")

        csv2 = df2.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Final CSV with Contextual Questions", csv2, file_name="tafsir_with_questions.csv", mime="text/csv")
