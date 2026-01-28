import os
import streamlit as st
import pandas as pd

from utils import (
    clean_dataframe,
    basic_summary,
    find_metric_column,
    top_categories,
    time_series_aggregate,
)

from chatbot import ask_ai  # make sure chatbot.py has ask_ai()
st.info("🤖 Chatbot is running in Demo Mode (offline) if Live API is unavailable. It still answers using real dataset stats.")


st.set_page_config(page_title="AI Data Analyst Assistant", layout="wide")
st.title("🤖 AI-Powered Data Analyst Assistant")
st.caption("Upload raw data → clean → insights → chat with your dataset")

# ---------- Sidebar navigation ----------
page = st.sidebar.radio("Navigation", ["🧹 Clean", "📈 Insights", "🤖 Chatbot"])

# ---------- Upload ----------
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV to begin.")
    st.stop()

# Performance: cache CSV load


@st.cache_data(show_spinner=False)
def load_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)


df = load_csv(uploaded_file)

# Use cleaned if available
working_df = st.session_state.get("cleaned_df", df)

# ---------- PAGE: CLEAN ----------
if page == "🧹 Clean":
    st.subheader("📊 Dataset Preview (Raw)")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("🧹 Step 1: Auto Data Cleaning")

    with st.expander("What cleaning is applied?", expanded=False):
        st.markdown(
            """
- Remove duplicate rows  
- Trim spaces in column names & text columns  
- Convert common 'null' strings to missing values  
- Convert date-like columns (if column name contains 'date')  
- Fill missing values:
  - Numeric → median
  - Text/categorical → mode (most frequent)
            """
        )

    if st.button("Run Auto Cleaning ✅"):
        cleaned_df, report = clean_dataframe(df)
        st.session_state["cleaned_df"] = cleaned_df
        st.session_state["clean_report"] = report
        st.success("Cleaning complete ✅")
        st.rerun()

    if "cleaned_df" in st.session_state:
        cleaned_df = st.session_state["cleaned_df"]
        report = st.session_state["clean_report"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows (before → after)",
                  f"{report['rows_before']} → {report['rows_after']}")
        c2.metric("Missing cells",
                  f"{report['missing_before']} → {report['missing_after']}")
        c3.metric(
            "Duplicates", f"{report['duplicates_before']} → {report['duplicates_after']}")
        c4.metric(
            "Columns", f"{report['cols_before']} → {report['cols_after']}")

        st.subheader("✅ Cleaned Preview")
        st.dataframe(cleaned_df.head(20), use_container_width=True)

        csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv_bytes,
            file_name="cleaned_data.csv",
            mime="text/csv",
        )

        st.divider()
        st.subheader("🧾 Cleaning Summary")
        st.markdown(
            f"""
- **Rows Before:** {report['rows_before']}
- **Rows After:** {report['rows_after']}
- **Columns Before:** {report['cols_before']}
- **Columns After:** {report['cols_after']}
- **Missing Values Before:** {report['missing_before']}
- **Missing Values After:** {report['missing_after']}
- **Duplicate Rows Before:** {report['duplicates_before']}
- **Duplicate Rows After:** {report['duplicates_after']}
            """
        )
    else:
        st.info("Click **Run Auto Cleaning ✅** to generate cleaned data and report.")

# ---------- PAGE: INSIGHTS ----------
elif page == "📈 Insights":
    st.subheader("📈 Step 2: Insights & Charts (Auto + Manual)")
    summary = basic_summary(working_df)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", summary["rows"])
    m2.metric("Columns", summary["cols"])
    m3.metric("Missing cells", summary["missing_cells"])
    m4.metric("Duplicate rows", summary["duplicate_rows"])

    num_cols = summary["num_cols"]
    cat_cols = summary["cat_cols"]
    date_cols = summary["date_cols"]

    with st.expander("Detected column types"):
        st.write("Numeric:", num_cols)
        st.write("Categorical:", cat_cols)
        st.write("Date:", date_cols)

    mode = st.radio("Choose chart mode", [
                    "Auto (recommended)", "Manual (choose columns)"], horizontal=True)

    if mode.startswith("Auto"):
        st.markdown("### 🤖 Auto Insights")
        metric_col = find_metric_column(working_df)
        st.write("**Detected main metric:**",
                 metric_col if metric_col else "No numeric metric found")

        # Numeric distributions
        if num_cols:
            st.markdown("#### Numeric distributions")
            for col in num_cols[:2]:
                st.write(f"**{col}**")
                st.bar_chart(working_df[col].value_counts(
                    bins=30).sort_index())

        # Top categories
        if cat_cols:
            st.markdown("#### Top categories")
            cat = cat_cols[0]
            top_df = top_categories(working_df, cat, n=10)
            st.write(f"**Top 10 for:** {cat}")
            st.dataframe(top_df, use_container_width=True)
            st.bar_chart(top_df.set_index(cat)["category_count"])

        # Time trend
        if date_cols and metric_col:
            st.markdown("#### Time trend")
            date_col = date_cols[0]
            ts = time_series_aggregate(
                working_df, date_col, metric_col, freq="M", agg="sum")
            if ts is not None and len(ts) > 1:
                ts = ts.rename(columns={date_col: "date"})
                st.line_chart(ts.set_index("date")[metric_col])
            else:
                st.info("Not enough valid date values to build a trend chart.")

        st.success("Auto insights generated ✅")

    else:
        st.markdown("### 🎛️ Manual Charts")
        chart_type = st.selectbox(
            "Choose chart type",
            ["Bar (Top categories)", "Line (Time trend)",
             "Histogram (Numeric distribution)"],
        )

        if chart_type.startswith("Bar"):
            if not cat_cols:
                st.warning("No categorical columns detected.")
            else:
                cat = st.selectbox("Choose category column", cat_cols)
                n = st.slider("Top N", 5, 30, 10)
                top_df = top_categories(working_df, cat, n=n)
                st.dataframe(top_df, use_container_width=True)
                st.bar_chart(top_df.set_index(cat)["category_count"])

        elif chart_type.startswith("Line"):
            if not date_cols:
                st.warning(
                    "No date columns detected. Tip: include 'date' in the column name.")
            else:
                date_col = st.selectbox("Choose date column", date_cols)
                if not num_cols:
                    st.warning(
                        "No numeric columns available for trend metric.")
                else:
                    metric_col = st.selectbox("Choose metric column", num_cols)
                    freq = st.selectbox(
                        "Frequency", ["D", "W", "M", "Q", "Y"], index=2)
                    agg = st.selectbox("Aggregation", ["sum", "mean"], index=0)

                    ts = time_series_aggregate(
                        working_df, date_col, metric_col, freq=freq, agg=agg)
                    if ts is not None and len(ts) > 1:
                        ts = ts.rename(columns={date_col: "date"})
                        st.line_chart(ts.set_index("date")[metric_col])
                    else:
                        st.info(
                            "Not enough valid date values to build a trend chart.")

        else:
            if not num_cols:
                st.warning("No numeric columns detected.")
            else:
                col = st.selectbox("Choose numeric column", num_cols)
                bins = st.slider("Bins", 10, 100, 30)
                st.bar_chart(working_df[col].value_counts(
                    bins=bins).sort_index())

# ---------- PAGE: CHATBOT ----------
else:
    st.subheader("🤖 Chat with your dataset")

    if not os.getenv("OPENAI_API_KEY"):
        st.warning(
            "OPENAI_API_KEY not found. Set it in your environment variables and restart VS Code.")
        st.stop()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_q = st.chat_input(
        "Ask about the dataset (e.g., issues, insights, trends, summary)…")
    if user_q:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)

        with st.chat_message("assistant"):
            with st.spinner("Thinking like a data analyst..."):
                answer = ask_ai(user_q, working_df,
                                st.session_state.chat_history)
                st.markdown(answer)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer})

    st.divider()
    if st.button("🧹 Clear chat"):
        st.session_state.chat_history = []
        st.rerun()
