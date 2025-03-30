import streamlit as st
import pandas as pd
import json
import requests

def run_combined_improvement(model_name, api_url, api_key, headers):
    st.header("🕌 Combined Enrichment & Thematic Splitting")
    st.markdown(
        "This step first performs combined enrichment (e.g., transferring or generating core metadata) and then splits long commentary "
        "into thematic sections (150–200 words each) for each Commentary Group."
    )
    
    # --- Upload CSV ---
    uploaded_file = st.file_uploader("📂 Upload CSV for Combined Processing", type=["csv"], key="combined_improvement")
    if not uploaded_file:
        st.info("Please upload a CSV file.")
        return
    
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Data")
    st.dataframe(df.head())
    
    # --- Combined Enrichment Step ---
    # For example: ensure the CSV has a 'ThemeText' column. If not, copy 'English Commentary' to it.
    if "ThemeText" not in df.columns:
        if "English Commentary" in df.columns:
            df["ThemeText"] = df["English Commentary"]
        else:
            st.error("❌ Neither 'ThemeText' nor 'English Commentary' columns found!")
            return
    st.success("Combined enrichment completed (ThemeText column is set).")
    
    # --- Thematic Splitting (Improvement 3) ---
    st.markdown("## Thematic Splitting")
    # Ensure there is a grouping column
    if "Commentary Group" not in df.columns:
        st.error("❌ 'Commentary Group' column not found in the CSV!")
        return
    
    grouped = df.groupby("Commentary Group")
    result_df = pd.DataFrame()  # to store new rows (one per thematic section)
    
    for group_name, group_df in grouped:
        st.markdown(f"### Processing Group: `{group_name}`")
        # Get the commentary text from the first non-empty row in the group
        commentary_series = group_df["English Commentary"].dropna().astype(str)
        commentary = commentary_series.iloc[0] if not commentary_series.empty else ""
        if not commentary:
            st.warning(f"No commentary found for group: {group_name}")
            continue
        
        # Build the prompt for thematic splitting
        prompt = f"""
Split the following commentary into thematic sections (150–200 words each). For each section, extract:
- SectionNumber (e.g., 1, 2, 3, …)
- ThemeTitle (short, descriptive)
- ThemeText (exact substring from the commentary, 150–200 words)
- ContextualQuestion (a deep, open-ended question)
- ThemeSummary (2–3 sentence overview)
- Keywords (5–7 key terms)
- Outline (3–5 bullet points)

Return the result as a JSON array where each item represents one section.

Commentary:
{commentary}
"""
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
            "max_tokens": 1200
        }
        
        try:
            with st.spinner(f"Splitting group {group_name}..."):
                response = requests.post(api_url, headers=headers, json=payload, timeout=90)
                reply = response.json()
                raw_content = reply["choices"][0]["message"]["content"]
                st.code(raw_content, language="json")
                
                # Clean up response (remove any markdown code fences)
                cleaned = raw_content.strip().replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned)
                
                # For each section returned, create a new row in result_df
                for section in data:
                    new_row = {}
                    # Copy all base columns from the first row of the group
                    for col in df.columns:
                        new_row[col] = group_df.iloc[0][col]
                    section_num = section.get("SectionNumber", "")
                    new_row["SectionNumber"] = f"{group_name} - Section {section_num}"
                    new_row["ThemeTitle"] = section.get("ThemeTitle", "")
                    new_row["ThemeText"] = section.get("ThemeText", "")
                    new_row["ContextualQuestion"] = section.get("ContextualQuestion", "")
                    new_row["ThemeSummary"] = section.get("ThemeSummary", "")
                    kw = section.get("Keywords", [])
                    new_row["Keywords"] = ", ".join(kw) if isinstance(kw, list) else str(kw)
                    ol = section.get("Outline", [])
                    new_row["Outline"] = "; ".join(ol) if isinstance(ol, list) else str(ol)
                    
                    result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)
        except Exception as e:
            st.warning(f"Failed for group {group_name}: {e}")
    
    st.success("Thematic splitting completed!")
    st.subheader("Preview of Combined Output:")
    st.dataframe(result_df.head())
    
    # Provide a download button for the final CSV
    csv_data = result_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Combined Enriched CSV", csv_data, file_name="combined_enrichment_and_split.csv", mime="text/csv")
