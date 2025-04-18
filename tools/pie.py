import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import re

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def extract_column_and_filter(query, df):
    numeric_cols = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
    all_cols = df.columns.tolist()

    target_col = None
    filter_key = None
    filter_value = None

    norm_query = normalize(query)

    for col in numeric_cols:
        if normalize(col) in norm_query:
            target_col = col
            break

    for col in all_cols:
        if df[col].dtype == "object":
            for val in df[col].unique():
                if normalize(str(val)) in norm_query:
                    filter_key = col
                    filter_value = val
                    break

    return target_col, filter_key, filter_value

def plot_pie(df: pd.DataFrame, query: str = ""):
    st.subheader("Pie Chart")

    col, filter_key, filter_val = extract_column_and_filter(query, df)

    if filter_key and filter_val:
        df = df[df[filter_key] == filter_val]
        st.success(f"Filtered data for `{filter_key}` = `{filter_val}`")

    query_lower = query.lower()
    show_record_counts = "record" in query_lower or "percentage" in query_lower

    if show_record_counts:
        # Try to find a grouping column
        possible_group_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        st.info("Query indicates percentage of records. Showing distribution by category.")
        group_col = None

        for col_name in possible_group_cols:
            if normalize(col_name) in normalize(query):
                group_col = col_name
                break

        if not group_col:
            group_col = st.selectbox("Select a categorical column to count records", possible_group_cols)

        value_counts = df[group_col].value_counts()
        if len(value_counts) > 20:
            st.warning("Too many unique values to show in pie chart. Showing top 10 by frequency.")
            value_counts = value_counts.nlargest(10)

        labels = value_counts.index
        values = value_counts.values
        title = f"Distribution of records by `{group_col}`"

    else:
        if not col:
            st.warning("Could not identify a numeric column to plot from the query.")
            col = st.selectbox("Select a numeric column to plot", df.select_dtypes(include=["float64", "int64"]).columns)

        unique_vals = set(df[col].dropna().unique())
        is_binary = unique_vals.issubset({0, 1})

        if is_binary:
            if any(key in col.lower() for key in ["sex", "gender"]):
                label_map = {0: "Male", 1: "Female"}
            else:
                label_map = {0: "No", 1: "Yes"}
            mapped_series = df[col].map(label_map)
            value_counts = mapped_series.value_counts()
            labels = value_counts.index
            values = value_counts.values
        else:
            if df[col].nunique() > 20:
                st.warning("Too many unique values to show in pie chart. Showing top 10 by frequency.")
                value_counts = df[col].value_counts().nlargest(10)
            else:
                value_counts = df[col].value_counts()
            labels = value_counts.index
            values = value_counts.values

        title = f"Pie chart of `{col}`" + (f" in `{filter_val}`" if filter_val else "")

    # Plotting with smaller fonts
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        textprops=dict(fontsize=10)  # Smaller font
    )
    ax.set_title(title, fontsize=12)
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(9)

    st.pyplot(fig)
