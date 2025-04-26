import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re

def normalize(text):
    subscripts = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    text = text.translate(subscripts)
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def extract_column_from_query(query: str, df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    norm_query = normalize(query)

    for col in numeric_cols:
        if normalize(col) == norm_query:
            return col

    candidates = [col for col in numeric_cols if normalize(col) in norm_query]
    if candidates:
        return max(candidates, key=lambda c: len(normalize(c)))
    return None

def get_time_column(df: pd.DataFrame):
    for col in df.columns:
        if 'date' in col.lower():
            return col
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    return None

def determine_time_aggregation(query: str):
    query = query.lower()
    if "monthly" in query or "month" in query:
        return 'M'
    elif "yearly" in query or "annual" in query or "year" in query:
        return 'Y'
    return 'D'  # default daily

def find_matching_value(query: str, options: list):
    """Tries to find a value from options mentioned in the query."""
    norm_query = normalize(query)
    for val in options:
        if normalize(val) in norm_query:
            return val
    return None

def plot_line(df: pd.DataFrame, query: str = ""):
    st.subheader("📈 Trend Over Time")

    y_col = extract_column_from_query(query, df)
    if not y_col:
        st.warning("❗Couldn't detect a numeric column to plot.")
        y_col = st.selectbox("👉 Select a numeric column", df.select_dtypes(include=["float64", "int64"]).columns)

    time_col = get_time_column(df)
    if not time_col:
        st.warning("❗Couldn't detect a date/time column.")
        time_col = st.selectbox("👉 Select a time column", df.columns)
    else:
        st.success(f"✅ Using `{time_col}` as the time axis")

    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col, y_col]).sort_values(time_col)

    # 🆕 Add dropdown for Daily/Monthly/Yearly
    agg_map = {'Daily': 'D', 'Monthly': 'M', 'Yearly': 'Y'}
    default_agg = determine_time_aggregation(query)
    agg_display = {'D': 'Daily', 'M': 'Monthly', 'Y': 'Yearly'}[default_agg]

    agg_choice = st.selectbox("👉 Select time aggregation", options=['Daily', 'Monthly', 'Yearly'], index=['Daily', 'Monthly', 'Yearly'].index(agg_display))
    agg_level = agg_map[agg_choice]

    # ---- smart filtering based on query ----
    groupby_cols = [col for col in df.reset_index().columns if df.reset_index()[col].nunique() < 100 and df.reset_index()[col].dtype == 'object']
    selected_group_col = None
    selected_value = None

    if groupby_cols:
        for col in groupby_cols:
            options = df.reset_index()[col].dropna().unique().tolist()
            match = find_matching_value(query, options)
            if match:
                selected_group_col = col
                selected_value = match
                break

    if selected_group_col and selected_value:
        st.info(f"🔍 Showing data for `{selected_value}` in `{selected_group_col}`")
        df_filtered = df.reset_index()
        df_filtered = df_filtered[df_filtered[selected_group_col] == selected_value]
        df_filtered = df_filtered.set_index(time_col)
        df_agg = df_filtered[[y_col]].resample(agg_level).mean().reset_index()
        plot_title = f"{y_col} over time ({agg_choice}) for {selected_value}"
    else:
        df_agg = df[[y_col]].resample(agg_level).mean().reset_index()
        plot_title = f"{y_col} over time ({agg_choice})"

    # ---- plotting ----
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

    ax.set_title(plot_title, fontsize=16, color="#333333", pad=15)
    ax.set_xlabel("Time", fontsize=12, color="#444444")
    ax.set_ylabel(y_col, fontsize=12, color="#444444")

    ax.tick_params(axis='x', rotation=45, labelcolor="#555555")
    ax.tick_params(axis='y', labelcolor="#555555")

    fig.tight_layout()
    st.pyplot(fig)
