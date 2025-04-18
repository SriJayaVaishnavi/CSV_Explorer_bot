import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re

def normalize(text):
    """Normalize text by converting subscript digits and removing non-alphanumeric characters."""
    subscripts = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    text = text.translate(subscripts)
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def extract_column_from_query(query: str, df: pd.DataFrame):
    """Extract the numeric column from query by matching normalized names."""
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    norm_query = normalize(query)
    for col in numeric_cols:
        if normalize(col) in norm_query:
            return col
    return None

def get_time_column(df: pd.DataFrame):
    """Guess the time column based on name or datetime dtype."""
    for col in df.columns:
        if 'date' in col.lower():
            return col
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    return None

def determine_time_aggregation(query: str):
    """Determine aggregation level from the query string."""
    query = query.lower()
    if "monthly" in query or "month" in query:
        return 'M'
    elif "yearly" in query or "annual" in query or "year" in query:
        return 'Y'
    return 'D'  # Default: daily

def plot_line(df: pd.DataFrame, query: str = ""):
    st.subheader("📈 Trend Over Time")

    # Step 1: Identify Y-Axis
    y_col = extract_column_from_query(query, df)
    if not y_col:
        st.warning("❗Couldn't automatically detect a numeric column to plot.")
        y_col = st.selectbox("👉 Select a numeric column", df.select_dtypes(include=["float64", "int64"]).columns)

    # Step 2: Identify Time Column
    time_col = get_time_column(df)
    if not time_col:
        st.warning("❗Couldn't automatically detect a date/time column.")
        time_col = st.selectbox("👉 Select a time column", df.columns)
    else:
        st.success(f"✅ Using `{time_col}` as the time axis")

    # Step 3: Clean & Prepare Data
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col, y_col]).sort_values(time_col)

    agg_level = determine_time_aggregation(query)
    df.set_index(time_col, inplace=True)
    df_agg = df[[y_col]].resample(agg_level).mean().reset_index()

    # Step 4: Plot with Seaborn
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))

    sns.lineplot(
        data=df_agg,
        x=time_col,
        y=y_col,
        marker="o",
        color="mediumseagreen",
        ax=ax
    )

    ax.set_title(f"{y_col} over time ({'Daily' if agg_level=='D' else 'Monthly' if agg_level=='M' else 'Yearly'})",
                 fontsize=16, color="#333333", pad=15)
    ax.set_xlabel("Time", fontsize=12, color="#444444")
    ax.set_ylabel(y_col, fontsize=12, color="#444444")

    ax.tick_params(axis='x', rotation=45, labelcolor="#555555")
    ax.tick_params(axis='y', labelcolor="#555555")

    fig.tight_layout()
    st.pyplot(fig)
