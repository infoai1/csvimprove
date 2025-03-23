import streamlit as st
import pandas as pd
import json
import requests
import textwrap

def run_improvement3(model_name, api_url, api_key, headers):
    st.header("🧠 Improvement 3: Thematic Splitting into Sections (150–200 words)")
    improvement3_file = st.file_uploader("📂 Upload CSV from Improvement 2", type="csv", key="improvement3")

    if improvement3_file and st.button("🚀 Split Commentary into Thematic Sections"):
        df = pd.read_csv(improvement3_file)
        st.success("✅ File loaded!")
        st.dataframe(df.head())

        new_columns = [
            "SectionNumber", "ThemeTitle", "ThemeText", "ContextualQuestion",
            "ThemeSummary", "Keywords", "Outline"
        ]

        for col in new_columns:
            if col not in df.columns:
                df[col] = ""

        grouped = df.groupby("Commentary Group")
        group_results = {}

        for group_name, group_df in grouped:
            st.markdown(f"### 📘 Processing Group: `{group_name}` for thematic sections")

            commentary_series = group_df["English Commentary"].dropna().astype(str)
            commentary = commentary_series.iloc[0] if not commentary_series.empty else ""

            if not commentary:
                continue

            prompt = f"""Split the following commentary into thematic sections (150–200 words each). For each section, extract:

- SectionNumber (e.g., 1, 2, 3)
- ThemeTitle (short, descriptive)
- ThemeText (150–200 words)
- ContextualQuestion (a deep, open-ended question)
- ThemeSummary (2–3 sentence overview)
- Keywords (5–7 key terms)
- Outline (3–5 bullet points)

Return as JSON list like:
[
  {{
    "SectionNumber": 1,
    "ThemeTitle": "...",
    "ThemeText": "...",
    "ContextualQuestion": "...",
    "ThemeSummary": "...",
    "Keywords": ["..."],
    "Outline": ["..."]
  }},
  ...
]

Commentary:
"""
{commentary}
"""

            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4,
                "max_tokens": 1200
            }

            try:
                with st.spinner(f"Splitting group {group_name}..."):
                    response = requests.post(api_url, headers=headers, json=payload, timeout=90)
                    raw_content = response.json()["choices"][0]["message"]["content"]
                    st.code(raw_content, language="json")

                    cleaned = raw_content.strip().replace("```json", "").replace("```", "").strip()
                    data = json.loads(cleaned)

                    for section in data:
                        full_section_number = f"{group_name} - Section {section.get('SectionNumber', '')}"
                        df.loc[df["Commentary Group"] == group_name, "SectionNumber"] = full_section_number
                        df.loc[df["Commentary Group"] == group_name, "ThemeTitle"] = section.get("ThemeTitle", "")
                        df.loc[df["Commentary Group"] == group_name, "ThemeText"] = section.get("ThemeText", "")
                        df.loc[df["Commentary Group"] == group_name, "ContextualQuestion"] = section.get("ContextualQuestion", "")
                        df.loc[df["Commentary Group"] == group_name, "ThemeSummary"] = section.get("ThemeSummary", "")
                        df.loc[df["Commentary Group"] == group_name, "Keywords"] = ", ".join(section.get("Keywords", []))
                        df.loc[df["Commentary Group"] == group_name, "Outline"] = "; ".join(section.get("Outline", []))

            except Exception as e:
                st.warning(f"❌ Failed for group {group_name}: {e}")

        st.success("🎉 Commentary split into thematic sections!")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Enriched CSV with Sections", csv, file_name="enriched_step3.csv", mime="text/csv")
