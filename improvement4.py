import streamlit as st
import pandas as pd
import openai

def run_improvement4(embedding_model, embedding_api_url, api_key, headers):
    st.header("🔎 Embedding Quran Commentary Themes")
    st.markdown(
        "This app will add semantic embeddings to your CSV using OpenAI Embeddings API. "
        "It supports models like `text-embedding-3-small`. You can also generate an optional summary."
    )

    # Set OpenAI API key
    openai.api_key = api_key
    openai.api_base = "https://api.openai.com/v1"

    # Upload CSV
    uploaded_file = st.file_uploader("📂 Upload CSV (must include 'ThemeText')", type=["csv"], key="embed_step")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Uploaded Data")
        st.dataframe(df.head())

        if "ThemeText" not in df.columns:
            st.error("❌ 'ThemeText' column not found in the CSV!")
            return

        # Step 1: Generate Embeddings
        st.markdown("## 1) Generate Embeddings for 'ThemeText'")
        if st.button("🔮 Start Embedding"):
            with st.spinner("Embedding in progress..."):
                try:
                    texts = df["ThemeText"].fillna("").tolist()
                    response = openai.Embedding.create(
                        model=embedding_model,
                        input=texts
                    )
                    vectors = [item["embedding"] for item in response["data"]]
                    df["Embedding"] = vectors
                    st.success("✅ Embeddings added to 'Embedding' column")
                    st.dataframe(df.head())
                except Exception as e:
                    st.error(f"Embedding failed: {e}")
                    return

            # Download enriched CSV
            csv_with_embeddings = df.to_csv(index=False, line_terminator="\n").encode("utf-8")
            st.download_button(
                "⬇️ Download CSV with Embeddings",
                csv_with_embeddings,
                file_name="csv_with_embeddings.csv",
                mime="text/csv"
            )

        # Step 2: Optional - Embedding Summary via GPT
        st.markdown("## 2) Optional: Get Summary of Embeddings")
        if st.button("🧠 Generate Theme Summary (GPT-4)"):
            with st.spinner("Calling GPT..."):
                try:
                    prompt = (
                        "Based on the embeddings generated for the provided Quranic commentary themes, "
                        "summarize any patterns or groupings you observe. Keep it brief and thematic."
                    )
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an expert in Quranic theme analysis."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )
                    summary = response["choices"][0]["message"]["content"]
                    st.success("✅ Embedding Summary Generated")
                    st.markdown("### 📘 Summary:")
                    st.write(summary)
                except Exception as e:
                    st.error(f"Failed to generate summary: {e}")
