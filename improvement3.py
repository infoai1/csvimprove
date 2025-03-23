import streamlit as st
import pandas as pd
import json
import requests
import textwrap

def chunk_text_with_overlap(text, chunk_size=200, overlap_ratio=0.1):
    """
    Splits the input text into chunks of roughly chunk_size words,
    overlapping each chunk by overlap_ratio (e.g., 0.1 = 10% overlap).
    """
    words = text.split()
    overlap = int(chunk_size * overlap_ratio)
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i: i + chunk_size]
        chunks.append(" ".join(chunk))
        # Move forward by chunk_size minus the overlap words
        i += (chunk_size - overlap)
    return chunks

def run_improvement3(model_name, api_url, api_key, headers):
    st.header("🧠 Improvement 3: Hybrid Chunking (Deterministic + AI Metadata)")
    st.markdown(
        "This method splits the commentary using a deterministic, fixed word count approach (with 10% overlap) "
        "and then calls the AI to generate thematic metadata for each chunk, while preserving the exact text."
    )

    improvement3_file = st.file_uploader(
        "📂 Upload CSV from Improvement 2", 
        type="csv", 
        key="improvement3"
    )

    if improvement3_file and st.button("🚀 Run Hybrid Chunking"):
        df = pd.read_csv(improvement3_file)
        st.success("✅ File loaded!")
        st.dataframe(df.head())

        # Base columns from original CSV plus new metadata columns
        base_cols = list(df.columns)
        extra_cols = [
            "SectionNumber", "ThemeText", "ThemeTitle", "ThemeSummary",
            "ContextualQuestion", "Keywords", "Outline"
        ]
        result_cols = base_cols + extra_cols
        result_df = pd.DataFrame(columns=result_cols)

        # Process each group separately
        if "Commentary Group" not in df.columns:
            st.error("❌ No 'Commentary Group' column found! Please ensure your CSV has a 'Commentary Group' column.")
            return

        grouped = df.groupby("Commentary Group")
        for group_name, group_df in grouped:
            st.markdown(f"### 📘 Processing Group: `{group_name}`")
            commentary_series = group_df["English Commentary"].dropna().astype(str)
            commentary = commentary_series.iloc[0] if not commentary_series.empty else ""

            if not commentary:
                st.warning(f"No commentary found for group: {group_name}")
                continue

            # Use deterministic local chunking with 10% overlap
            chunks = chunk_text_with_overlap(commentary, chunk_size=200, overlap_ratio=0.1)
            st.write(f"Found {len(chunks)} chunk(s) for group {group_name} with 10% overlap.")

            for idx_chunk, chunk_text in enumerate(chunks, start=1):
                # Build the prompt for metadata generation
                prompt = f"""
You are given the following exact excerpt from a Quranic commentary (no paraphrasing allowed).
Please analyze the excerpt and provide the following metadata:
- ThemeTitle (1-5 words)
- ThemeSummary (2-3 sentences)
- Three ContextualQuestion covering context from available different perspectives like materialism , secularism , ritualistic way or any other (deep and open-ended)
- Keywords (5-7 keywords as a list)
- Outline (3-5 bullet points)

Return your result as JSON with keys: 
ThemeTitle, ThemeSummary, ContextualQuestion, Keywords, Outline.

Excerpt:
\"\"\"
{chunk_text}
\"\"\"
"""
                payload = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 800
                }
                try:
                    with st.spinner(f"Labeling chunk #{idx_chunk} in group {group_name}..."):
                        response = requests.post(api_url, headers=headers, json=payload, timeout=90)
                        reply = response.json()
                        raw_content = reply["choices"][0]["message"]["content"]
                        st.code(raw_content, language="json")

                        # Clean and parse the JSON response
                        cleaned = raw_content.strip().replace("```json", "").replace("```", "").strip()
                        try:
                            meta = json.loads(cleaned)
                        except json.JSONDecodeError as decode_err:
                            st.warning(f"❌ JSON parse error for chunk #{idx_chunk} in group {group_name}: {decode_err}")
                            meta = {}

                        # Build new row data (copy base group info from first row)
                        new_row = {}
                        for col in base_cols:
                            new_row[col] = group_df.iloc[0][col]

                        new_row["SectionNumber"] = f"{group_name} - Chunk {idx_chunk}"
                        new_row["ThemeText"] = chunk_text  # exact excerpt from commentary
                        new_row["ThemeTitle"] = meta.get("ThemeTitle", "")
                        new_row["ThemeSummary"] = meta.get("ThemeSummary", "")
                        new_row["ContextualQuestion"] = meta.get("ContextualQuestion", "")
                        
                        # Convert Keywords and Outline if they're lists
                        keywords_list = meta.get("Keywords", [])
                        if isinstance(keywords_list, list):
                            new_row["Keywords"] = ", ".join(keywords_list)
                        else:
                            new_row["Keywords"] = str(keywords_list)
                        
                        outline_list = meta.get("Outline", [])
                        if isinstance(outline_list, list):
                            new_row["Outline"] = "; ".join(outline_list)
                        else:
                            new_row["Outline"] = str(outline_list)

                        result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)
                except Exception as e:
                    st.warning(f"❌ Failed for chunk #{idx_chunk} in group {group_name}: {e}")

        st.success("🎉 All commentary chunks processed with 10% overlap!")
        st.write("Preview of final output:")
        st.dataframe(result_df.head())

        csv_data = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV with Hybrid Chunks",
            csv_data,
            file_name="enriched_step3_hybrid.csv",
            mime="text/csv"
        )
