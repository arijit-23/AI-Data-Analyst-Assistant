import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Data Analyst Assistant", layout="wide")
st.title("🤖 AI-Powered Data Analyst Assistant")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Dataset Preview")
    st.dataframe(df.head())

    st.subheader("📌 Dataset Info")
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")

    st.subheader("🧹 Missing Values")
    st.dataframe(df.isnull().sum())