import streamlit as st
import pandas as pd
import json
import requests
import textwrap

def run_improvement3(model_name, api_url, api_key, headers):
    st.header("🧠 Improvement 3: Thematic Splitting – Two Approaches")

    approach = st.radio(
        "Choose Splitting Approach:",
        ["Deterministic Local Chunking", "AI Thematic Splitting"]
    )

    improvement3_file = st.file_uploader("📂 Upload CSV from Improvement 2", type="csv", key="improvement3")

    if improvement3_file and st.button("🚀 Process Commentary"):
        df = pd.read_csv(improvement3_file)
        st.success("✅ File loaded!")
        st.dataframe(df.head())

        # Base columns
        base_cols = list(df.columns)

        # Additional columns for new rows
        extra_cols = [
            "SectionNumber",
            "ThemeText",        # exact chunk or AI snippet
            "ThemeTitle",
            "ThemeSummary",
            "ContextualQuestion",
            "Keywords",
            "Outline"
        ]

        # Final DataFrame with combined columns
        result_cols = base_cols + extra_cols
        result_df = pd.DataFrame(columns=result_cols)

        grouped = df.groupby("Commentary Group")

        for group_name, group_df in grouped:
            st.markdown(f"### 📘 Group: `{group_name}`")
            
            commentary_series = group_df["English Commentary"].dropna().astype(str)
            commentary = commentary_series.iloc[0] if not commentary_series.empty else ""
            
            if not commentary:
                st.warning(f"No commentary for group: {group_name}")
                continue

            if approach == "Deterministic Local Chunking":
                # -------------------------------------------------------
                # 1) LOCAL CHUNKING by word count (~200 words each)
                # -------------------------------------------------------
                chunk_size = 200

                # Break commentary into ~200-word segments
                words = commentary.split()
                chunks = []
                for i in range(0, len(words), chunk_size):
                    chunk_text = " ".join(words[i:i+chunk_size])
                    chunks.append(chunk_text)

                st.write(f"Found {len(chunks)} local chunk(s) for group {group_name}.")

                # 2) For each chunk, we call AI to label it with theme metadata
                for idx_chunk, chunk_text in enumerate(chunks, start=1):
                    prompt = f"""
You have this excerpt from a Quranic commentary. It is exactly one chunk of ~200 words. 
Please provide:
- ThemeTitle (1–5 words)
- ThemeSummary (2–3 sentences)
- One ContextualQuestion
- 5–7 Keywords
- Outline (3–5 bullet points)

Return JSON with keys: ThemeTitle, ThemeSummary, ContextualQuestion, Keywords, Outline

Excerpt:
\"\"\"
{chunk_text}
\"\"\"
"""
                    try:
                        with st.spinner(f"Local-chunk approach: labeling chunk #{idx_chunk} in {group_name}..."):
                            payload = {
                                "model": model_name,
                                "messages": [{"role": "user", "content": prompt}],
                                "temperature": 0.3,
                                "max_tokens": 800
                            }

                            response = requests.post(api_url, headers=headers, json=payload, timeout=90)
                            reply = response.json()
                            raw_content = reply["choices"][0]["message"]["content"]
                            st.code(raw_content, language="json")

                            # Clean & parse
                            cleaned = raw_content.strip().replace("```json", "").replace("```", "").strip()

                            try:
                                meta = json.loads(cleaned)
                            except json.JSONDecodeError as decode_err:
                                st.warning(f"❌ JSON parse failed for chunk #{idx_chunk} in group {group_name}: {decode_err}")
                                meta = {}

                            # Build new row
                            new_row = {}
                            # Copy base columns from the group's first row
                            for col in base_cols:
                                new_row[col] = group_df.iloc[0][col]

                            new_row["SectionNumber"] = f"{group_name} - Chunk {idx_chunk}"
                            new_row["ThemeText"] = chunk_text  # exact text
                            new_row["ThemeTitle"] = meta.get("ThemeTitle", "")
                            new_row["ThemeSummary"] = meta.get("ThemeSummary", "")
                            new_row["ContextualQuestion"] = meta.get("ContextualQuestion", "")

                            kw = meta.get("Keywords", [])
                            if isinstance(kw, list):
                                new_row["Keywords"] = ", ".join(kw)
                            else:
                                new_row["Keywords"] = str(kw)

                            ol = meta.get("Outline", [])
                            if isinstance(ol, list):
                                new_row["Outline"] = "; ".join(ol)
                            else:
                                new_row["Outline"] = str(ol)

                            result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)

                    except Exception as e:
                        st.warning(f"❌ Local-chunk approach failed for chunk #{idx_chunk}, group {group_name}: {e}")

            else:
                # -------------------------------------------------------
                # 2) AI THEMATIC SPLITTING (like your original approach)
                # -------------------------------------------------------
                prompt = f"""
Split the following commentary into THEMATIC sections (150–200 words each). 
For each section:
- SectionNumber (1, 2, 3,...)
- ThemeTitle (short, descriptive)
- ThemeText (EXACT substring, no paraphrasing, up to 200 words)
- ThemeSummary (2–3 sentences)
- ContextualQuestion (1 deep question)
- Keywords (5–7 key terms in an array)
- Outline (3–5 bullet points)

Return as JSON list, each item = one theme section.

Commentary:
\"\"\"
{commentary}
\"\"\"
"""
                try:
                    with st.spinner(f"AI-based thematic approach for {group_name}..."):
                        payload = {
                            "model": model_name,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.3,
                            "max_tokens": 1200
                        }

                        response = requests.post(api_url, headers=headers, json=payload, timeout=90)
                        reply = response.json()
                        raw_content = reply["choices"][0]["message"]["content"]
                        st.code(raw_content, language="json")

                        cleaned = raw_content.strip().replace("```json", "").replace("```", "").strip()

                        try:
                            data = json.loads(cleaned)
                        except json.JSONDecodeError as decode_err:
                            st.warning(f"❌ JSON parse error for group {group_name}: {decode_err}")
                            data = []

                        for section_dict in data:
                            new_row = {}
                            # Copy base columns from the group's first row
                            for col in base_cols:
                                new_row[col] = group_df.iloc[0][col]

                            s_num = section_dict.get("SectionNumber", "")
                            new_row["SectionNumber"] = f"{group_name} - Section {s_num}"
                            new_row["ThemeText"] = section_dict.get("ThemeText", "")
                            new_row["ThemeTitle"] = section_dict.get("ThemeTitle", "")
                            new_row["ThemeSummary"] = section_dict.get("ThemeSummary", "")
                            new_row["ContextualQuestion"] = section_dict.get("ContextualQuestion", "")

                            kw = section_dict.get("Keywords", [])
                            if isinstance(kw, list):
                                new_row["Keywords"] = ", ".join(kw)
                            else:
                                new_row["Keywords"] = str(kw)

                            ol = section_dict.get("Outline", [])
                            if isinstance(ol, list):
                                new_row["Outline"] = "; ".join(ol)
                            else:
                                new_row["Outline"] = str(ol)

                            result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)

                except Exception as e:
                    st.warning(f"❌ AI-based thematic approach failed for group {group_name}: {e}")

        st.success("🎉 All groups processed!")
        st.write("Preview of final output:")
        st.dataframe(result_df.head())

        csv_data = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Final CSV",
            csv_data,
            file_name="improvement3_output.csv",
            mime="text/csv"
        )
