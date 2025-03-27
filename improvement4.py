import streamlit as st
import pandas as pd
import openai

def run_improvement4(embedding_model, embedding_api_url, api_key, headers):
    """
    Improvement 4:
    1) Adds embeddings to CSV using the specified OpenAI Embeddings API.
    2) Lets the user compare selected rows' ThemeText with GPT-4.
    
    Parameters:
      - embedding_model: (str) e.g., "text-embedding-3-small" or "text-embedding-ada-002"
      - embedding_api_url: (str) The API endpoint for embeddings.
      - api_key: (str) Your OpenAI API key.
      - headers: (dict) Shared headers (includes the API key).
    """
    st.header("🔎 Improvement 4: Embeddings & Relationship Analysis")
    st.markdown(
        "This step adds an 'Embedding' column to your CSV using OpenAI Embeddings and optionally compares "
        "selected rows' ThemeText to analyze their relationship."
    )

    # Set OpenAI API key and base for embeddings
    openai.api_key = api_key
    openai.api_base = embedding_api_url

    # --- File Upload ---
    uploaded_file = st.file_uploader("📂 Upload your CSV file (must have 'ThemeText' column)", type=["csv"], key="improvement4")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Uploaded Data")
        st.dataframe(df.head())

        if "ThemeText" not in df.columns:
            st.error("❌ 'ThemeText' column not found in the CSV!")
            return

        # --- Step 1: Generate Embeddings ---
        st.markdown("## 1) Add OpenAI Embeddings to Each Row")
        if st.button("🔮 Generate Embeddings for 'ThemeText'"):
            with st.spinner("Generating embeddings..."):
                embeddings = []
                for idx, row in df.iterrows():
                    text = str(row["ThemeText"])
                    if not text.strip():
                        embeddings.append(None)
                        continue
                    try:
                        response = openai.Embedding.create(
                            model=embedding_model,
                            input=text
                        )
                        vector = response["data"][0]["embedding"]
                        embeddings.append(vector)
                    except Exception as e:
                        st.warning(f"Row {idx} failed to embed: {e}")
                        embeddings.append(None)

                df["Embedding"] = embeddings
                st.success("✅ Embeddings generated and stored in 'Embedding' column.")

            st.dataframe(df.head())

            csv_with_embeddings = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download CSV with Embeddings",
                csv_with_embeddings,
                file_name="csv_with_embeddings.csv",
                mime="text/csv"
            )

        # --- Step 2: Row-to-Row Comparison ---
        st.markdown("## 2) Compare Rows' ThemeText")
        st.info("Select 2 or more rows to compare their meanings with GPT-4.")
        selected_indices = st.multiselect("Choose 2 or more rows", options=df.index.tolist())

        if len(selected_indices) >= 2 and api_key:
            selected_texts = df.loc[selected_indices, 'ThemeText'].tolist()

            prompt = f"""You are analyzing Quranic commentary themes. Compare the following texts and determine whether their meanings are:
- Similar
- Complementary
- Contrary

Provide a relationship label for each pair and a short explanation.

Texts:
"""
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
                        temperature=0.3
                    )
                    ai_result = response['choices'][0]['message']['content']
                    st.success("✅ Analysis Complete")
                    st.markdown("### 🧾 Result from AI:")
                    st.write(ai_result)
                except Exception as e:
                    st.error(f"OpenAI GPT-4 call failed: {e}")

        elif len(selected_indices) > 0 and not api_key:
            st.warning("⚠️ Please enter your API key to proceed.")
        elif len(selected_indices) < 2:
            st.info("ℹ️ Select at least 2 rows to compare.")
