import streamlit as st
import pandas as pd
import openai
import json

def run_improvement4(embedding_model, embedding_api_url, api_key, headers):
    st.header("🔎 Improvement 4: Embeddings & Relationship Analysis")
    st.markdown(
        "This step adds an 'Embedding' column to your CSV using OpenAI Embeddings API and optionally compares "
        "selected rows' ThemeText to analyze their relationship."
    )

    # Set OpenAI API key and base (use default base URL)
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
                    st.success("✅ Embeddings added")
                    st.dataframe(df.head())
                except Exception as e:
                    st.error(f"Embedding failed: {e}")
                    return

            # Convert embedding vectors to JSON strings for CSV export
            try:
                df["Embedding"] = df["Embedding"].apply(lambda x: json.dumps(x) if pd.notnull(x) else "")
                csv_with_embeddings = df.to_csv(index=False, line_terminator="\n").encode("utf-8")
                st.download_button(
                    "⬇️ Download CSV with Embeddings",
                    csv_with_embeddings,
                    file_name="csv_with_embeddings.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Failed to export CSV: {e}")

        # --- Step 2: Row-to-Row Comparison ---
        st.markdown("## 2) Compare Rows' ThemeText")
        st.info("Select 2 or more rows to compare their meanings with GPT-4.")
        selected_indices = st.multiselect("Choose 2 or more rows", options=df.index.tolist())

        if len(selected_indices) >= 2 and api_key:
            selected_texts = df.loc[selected_indices, "ThemeText"].tolist()
            prompt = """You are analyzing Quranic commentary themes. Compare the following texts and determine whether their meanings are:
- Similar
- Complementary
- Contrary

Provide a relationship label for each pair and a short explanation.

Texts:"""
            for i, text in enumerate(selected_texts, 1):
                prompt += f"\nText {i}: {text.strip()}\n"

            with st.spinner("Analyzing with GPT-4..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a Quranic scholar and theme analyzer."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=250
                    )
                    ai_result = response["choices"][0]["message"]["content"]
                    st.success("✅ Analysis Complete")
                    st.markdown("### 🧾 Result from AI:")
                    st.write(ai_result)
                except Exception as e:
                    st.error(f"GPT-4 call failed: {e}")
        elif len(selected_indices) > 0 and not api_key:
            st.warning("⚠️ Please enter your API key to proceed.")
        elif len(selected_indices) < 2:
            st.info("ℹ️ Select at least 2 rows to compare.")
