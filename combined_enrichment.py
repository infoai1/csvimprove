import streamlit as st
import pandas as pd
import json
import requests

def run_combined_enrichment(model_name, api_url, api_key, headers):
    st.header("📚 Combined Enrichment Tool")
    uploaded_file = st.file_uploader("📂 Upload Tafsir CSV", type="csv", key="combined")

    # 🔘 Choose mode
    mode = st.radio("Select what to run:", [
        "🔹 Only Themes, Wisdom, Reflections",
        "🔸 Only Outline & Contextual Questions",
        "🧩 Run Both Together"
    ])

    if uploaded_file and st.button("🚀 Run Enrichment"):
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()
        st.success("✅ File loaded!")
        st.dataframe(df.head())

        # Check required columns
        required_cols = ["Verse Group", "translation", "English Commentary"]
        if any(col not in df.columns for col in required_cols):
            st.error(f"❌ Missing one of the required columns: {required_cols}")
            return

        # Fields by section
        enrich_fields_part1 = ["themes", "wisdom_points", "real_life_reflections", "revelation_context"]
        enrich_fields_part2 = ["outline_of_commentary", "contextual_questions"]
        enrich_fields = []

        if "Only Themes" in mode or "Both" in mode:
            enrich_fields += enrich_fields_part1
        if "Only Outline" in mode or "Both" in mode:
            enrich_fields += enrich_fields_part2

        for field in enrich_fields:
            if field not in df.columns:
                df[field] = ""

        grouped = df.groupby("Verse Group")
        results = {}

        for group_name, group_df in grouped:
            st.markdown(f"### 🧠 Processing Group: `{group_name}`")

            translation = " | ".join(group_df["translation"].dropna().astype(str).tolist())
            commentary_series = group_df["English Commentary"].dropna().astype(str)
            commentary = commentary_series.iloc[0] if not commentary_series.empty else "No commentary provided."

            # Prompt template
            prompt_parts = []
            if "Only Themes" in mode or "Both" in mode:
                prompt_parts.append("1. themes\n2. wisdom_points\n3. real_life_reflections\n4. revelation_context")
            if "Only Outline" in mode or "Both" in mode:
                prompt_parts.append("5. outline_of_commentary – bullet summary\n6. contextual_questions – 4–6 explanations")

            prompt = f"""
Given this Quranic translation: "{translation}"  
and commentary: "{commentary}", extract:

{chr(10).join(prompt_parts)}

Return result as valid JSON including only the fields requested.
"""

            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
                "max_tokens": 1000
            }

            try:
                with st.spinner(f"Processing group: {group_name}..."):
                    response = requests.post(api_url, headers=headers, json=payload, timeout=90)
                    content = response.json()["choices"][0]["message"]["content"]
                    cleaned = content.strip().replace("```json", "").replace("```", "").strip()
                    result = json.loads(cleaned)
                    st.code(json.dumps(result, indent=2), language="json")
                    results[group_name] = result
            except Exception as e:
                st.warning(f"⚠️ Failed for group '{group_name}': {e}")
                results[group_name] = {field: "" for field in enrich_fields}

        # Apply results
        for idx, row in df.iterrows():
            enriched = results.get(row["Verse Group"], {})
            for field in enrich_fields:
                df.at[idx, field] = enriched.get(field, "")

        st.success("🎉 Enrichment Complete!")
        enriched_csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Enriched CSV", enriched_csv, file_name="enriched_combined.csv", mime="text/csv")
