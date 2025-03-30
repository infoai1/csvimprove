import streamlit as st
import pandas as pd
import openai
import json

def run_improvement4(embedding_model, embedding_api_url, api_key, headers):
    st.header("🔎 Improvement 4: Embeddings for ThemeText")
    st.markdown(
        "This step adds an 'Embedding' column to your CSV using OpenAI's Embeddings API. "
        "It supports models like `text-embedding-3-small` or `text-embedding-ada-002`."
    )

    # Set OpenAI API key and base (use the default base)
    openai.api_key = api_key
    openai.api_base = "https://api.openai.com/v1"

    # --- File Upload ---
    uploaded_file = st.file_uploader("📂 Upload your CSV file (must include 'ThemeText' column)", type=["csv"], key="improvement4")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Uploaded Data")
        st.dataframe(df.head())

        if "ThemeText" not in df.columns:
            st.error("❌ 'ThemeText' column not found in the CSV!")
            return

        # --- Step 1: Generate Embeddings for ThemeText ---
        st.markdown("## 1) Generate Embeddings for 'ThemeText'")
        if st.button("🔮 Start Embedding"):
            with st.spinner("Generating embeddings..."):
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

            # Convert embedding vectors to JSON strings for CSV export
            try:
                df["Embedding"] = df["Embedding"].apply(
                    lambda x: json.dumps(x.tolist()) if hasattr(x, "tolist") 
                              else json.dumps(x) if isinstance(x, (list, tuple))
                              else ""
                )
                csv_with_embeddings = df.to_csv(index=False, line_terminator="\n").encode("utf-8")
                st.download_button(
                    "⬇️ Download CSV with Embeddings",
                    csv_with_embeddings,
                    file_name="csv_with_embeddings.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Failed to export CSV: {e}")
