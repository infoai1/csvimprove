import streamlit as st
import pandas as pd
import requests
import json

def run_improvement5(model_name, api_url, api_key, headers):
    """
    Stepwise enrichment:
    1) Chapter-level: summary, outline, contextual questions based on 'Detected Title'.
    2) Chunk-level: wisdom, reflections, outline, contextual questions for each 'TEXT CHUNK'.
    """
    st.header("📖 Improvement 5: Chapter & Chunk Enrichment")
    uploaded = st.file_uploader("📂 Upload your CSV", type="csv", key="improve5")
    if not uploaded:
        return
    if st.button("🚀 Enrich Chapters & Chunks"):
        df = pd.read_csv(uploaded)
        st.success("✅ CSV loaded!")
        # Initialize new columns
        df["ChapterSummary"] = ""
        df["ChapterOutline"] = ""
        df["ChapterQuestions"] = ""
        df["Wisdom"] = ""
        df["Reflections"] = ""
        df["ChunkOutline"] = ""
        df["ChunkQuestions"] = ""

        # Chapter-level enrichment
        for title in df["Detected Title"].unique():
            prompt = (
                f"Summarize the chapter titled '{title}' in 50 words. "
                "Provide an outline of 3-5 bullet points, and 2 contextual questions. "
                "Return the output as JSON with keys: ChapterSummary, ChapterOutline, ChapterQuestions."
            )
            res = requests.post(
                api_url,
                headers=headers,
                json={"model": model_name,
                      "messages": [{"role": "user", "content": prompt}]}
            )
            data = res.json()["choices"][0]["message"]["content"]
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                st.error(f"Invalid JSON for chapter '{title}': {data}")
                continue
            mask = df["Detected Title"] == title
            df.loc[mask, "ChapterSummary"] = obj.get("ChapterSummary", "")
            df.loc[mask, "ChapterOutline"] = json.dumps(obj.get("ChapterOutline", []))
            df.loc[mask, "ChapterQuestions"] = json.dumps(obj.get("ChapterQuestions", []))

        # Chunk-level enrichment
        for idx, row in df.iterrows():
            chunk = row.get("TEXT CHUNK", "")
            prompt = (
                f"For the following text chunk, generate Wisdom, Reflections, "
                "an outline (3-5 bullets), and 1 contextual question. "
                f"Text Chunk: {chunk}" 
                "Return JSON with keys: Wisdom, Reflections, ChunkOutline, ChunkQuestions."
            )
            res = requests.post(
                api_url,
                headers=headers,
                json={"model": model_name,
                      "messages": [{"role": "user", "content": prompt}]}
            )
            data = res.json()["choices"][0]["message"]["content"]
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                st.error(f"Invalid JSON for chunk idx {idx}: {data}")
                continue
            df.at[idx, "Wisdom"] = obj.get("Wisdom", "")
            df.at[idx, "Reflections"] = obj.get("Reflections", "")
            df.at[idx, "ChunkOutline"] = json.dumps(obj.get("ChunkOutline", []))
            df.at[idx, "ChunkQuestions"] = json.dumps(obj.get("ChunkQuestions", []))

        # Download enriched CSV
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Fully Enriched CSV",
            csv_data,
            file_name="enriched_full.csv",
            mime="text/csv"
        )
