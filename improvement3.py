import streamlit as st
import pandas as pd
import json
import requests
import textwrap

# Improvement 3: Thematic Splitting, each new section => new row

def run_improvement3(model_name, api_url, api_key, headers):
    st.header("🧠 Improvement 3: Thematic Splitting into Sections (150–200 words)")
    improvement3_file = st.file_uploader("📂 Upload CSV from Improvement 2", type="csv", key="improvement3")

    if improvement3_file and st.button("🚀 Split Commentary into Thematic Sections"):
        df = pd.read_csv(improvement3_file)
        st.success("✅ File loaded!")
        st.dataframe(df.head())

        # We'll create a new DataFrame to store the results (one row per section)
        columns_needed = list(df.columns) + [
            "SectionNumber", "ThemeTitle", "ThemeText", "ContextualQuestion",
            "ThemeSummary", "Keywords", "Outline"
        ]

        # Guarantee they exist in the final result
        # but the new DF will have them as columns
        result_df = pd.DataFrame(columns=columns_needed)

        # Group by 'Commentary Group' as usual
        grouped = df.groupby("Commentary Group")

        for group_name, group_df in grouped:
            st.markdown(f"### 📘 Processing Group: `{group_name}` for thematic sections")

            commentary_series = group_df["English Commentary"].dropna().astype(str)
            commentary = commentary_series.iloc[0] if not commentary_series.empty else ""

            if not commentary:
                continue

            # Build the prompt
            prompt = f"""
Split the following commentary into thematic sections (150–200 words each). For each section, extract:
- SectionNumber (1, 2, 3,...)
- ThemeTitle (short, descriptive)
- ThemeText (150–200 words)
- ContextualQuestion (a deep, open-ended question)
- ThemeSummary (2–3 sentence overview)
- Keywords (5–7 key terms)
- Outline (3–5 bullet points)

Return as JSON list, each item = one section.

Commentary:
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
                    reply = response.json()
                    raw_content = reply["choices"][0]["message"]["content"]
                    st.code(raw_content, language="json")

                    # Parse the JSON array
                    cleaned = raw_content.strip().replace("```json", "").replace("```", "").strip()
                    data = json.loads(cleaned)

                    # For each returned section, create a new row in result_df
                    for section in data:
                        new_row = {}

                        # Copy over the existing group's first row data if needed
                        # Or we can copy from group_df.iloc[0] to preserve columns
                        for col in df.columns:
                            new_row[col] = group_df.iloc[0][col]

                        # Now set the new section fields
                        section_num = section.get("SectionNumber", "")
                        new_row["SectionNumber"] = f"{group_name} - Section {section_num}"
                        new_row["ThemeTitle"] = section.get("ThemeTitle", "")
                        new_row["ThemeText"] = section.get("ThemeText", "")
                        new_row["ContextualQuestion"] = section.get("ContextualQuestion", "")
                        new_row["ThemeSummary"] = section.get("ThemeSummary", "")
                        new_row["Keywords"] = ", ".join(section.get("Keywords", []))
                        new_row["Outline"] = "; ".join(section.get("Outline", []))

                        result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)

            except Exception as e:
                st.warning(f"❌ Failed for group {group_name}: {e}")

        st.success("🎉 Commentary successfully split into new rows!")
        st.write("Preview:")
        st.dataframe(result_df.head())

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV with Thematic Sections (New Rows)", csv, file_name="enriched_step3_newrows.csv", mime="text/csv")
