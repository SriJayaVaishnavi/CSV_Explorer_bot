import streamlit as st
import seaborn as sns
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

def normalize(text):
    """Normalize text, including subscript to digit mapping."""
    if not isinstance(text, str):
        text = str(text)
    subscripts = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    text = text.translate(subscripts)
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def extract_numeric_column(query: str, df: pd.DataFrame):
    """Extract numeric column from query based on semantic matching."""
    numeric_cols = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
    if not numeric_cols:
        return None

    norm_query = normalize(query)
    query_words = set(word.strip() for word in query.lower().split())

    measure_keywords = ["average", "mean", "total", "sum", "count", "number", "amount", "level", "value", "quantity"]
    query_words = query_words - set(measure_keywords)

    best_match = None
    best_score = 0

    for col in numeric_cols:
        score = 0
        col_name = col.lower()
        norm_col = normalize(col)

        if norm_col in norm_query:
            score += 3

        col_parts = set(word.strip() for word in col_name.split())
        matching_parts = col_parts.intersection(query_words)
        score += len(matching_parts) * 2

        for word in query_words:
            if word in col_name:
                score += 1

        if score > best_score:
            best_score = score
            best_match = col

    return best_match

def extract_categorical_column(query: str, df: pd.DataFrame):
    """Extract categorical column from query based on context and common patterns."""
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not categorical_cols:
        return None

    norm_query = normalize(query)
    query_lower = query.lower()

    grouping_patterns = [
        ("group by", 3),
        ("grouped by", 3),
        ("split by", 3),
        ("break down by", 3),
        ("categorize by", 3),
        ("categorized by", 3),
        ("per", 2),
        ("for each", 2),
        ("across", 2),
        ("by", 1),
        ("in", 1),
        ("at", 1)
    ]

    category_indicators = [
        ("type", 2),
        ("category", 2),
        ("class", 2),
        ("group", 2),
        ("name", 2),
        ("id", 1),
        ("code", 1),
        ("status", 2),
        ("level", 1),
        ("grade", 1)
    ]

    best_match = None
    best_score = 0

    for col in categorical_cols:
        score = 0
        col_lower = col.lower()

        for pattern, pattern_score in grouping_patterns:
            if pattern in query_lower:
                after_pattern = query_lower.split(pattern)[-1].strip()
                if normalize(col) in normalize(after_pattern):
                    score += pattern_score * 2

        for indicator, indicator_score in category_indicators:
            if indicator in col_lower:
                score += indicator_score

        if normalize(col) in norm_query:
            score += 3

        col_parts = set(word.strip() for word in col_lower.split())
        query_parts = set(word.strip() for word in query_lower.split())
        matching_parts = col_parts.intersection(query_parts)
        score += len(matching_parts)

        if score > best_score:
            best_score = score
            best_match = col

    return best_match

def determine_aggregation(query: str):
    """Determine the aggregation method from query context."""
    query = query.lower()

    aggregations = {
        "mean": ["average", "mean", "avg", "typical", "expected"],
        "sum": ["total", "sum", "overall", "combined", "aggregate"],
        "count": ["count", "number of", "frequency", "occurrences", "instances"],
        "max": ["maximum", "max", "highest", "peak", "greatest", "top"],
        "min": ["minimum", "min", "lowest", "bottom", "least"],
        "median": ["median", "middle", "mid", "50th percentile"],
        "std": ["standard deviation", "std", "variation", "spread", "dispersion"]
    }

    scores = {method: 0 for method in aggregations}

    for method, keywords in aggregations.items():
        for keyword in keywords:
            if keyword in query:
                scores[method] += 1
                if f" {keyword} " in f" {query} ":
                    scores[method] += 1

    best_method = max(scores.items(), key=lambda x: x[1])[0]
    return best_method if scores[best_method] > 0 else "mean"

def plot_bar(df: pd.DataFrame, query: str = ""):
    """Create a styled bar chart based on the query."""
    st.subheader("Bar Chart")

    if df.empty:
        st.warning("No data available for plotting.")
        return

    numeric_col = extract_numeric_column(query, df)
    group_col = extract_categorical_column(query, df)

    if not numeric_col:
        numeric_cols = df.select_dtypes(include=["float64", "int64", "int32"]).columns
        if len(numeric_cols) == 0:
            st.error("No numeric columns found in the dataset.")
            return
        numeric_col = st.selectbox("Select a numeric column to plot:", numeric_cols)

    if not group_col:
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns
        if len(categorical_cols) == 0:
            st.error("No categorical columns found for grouping.")
            return
        group_col = st.selectbox("Select a column to group by:", categorical_cols)

    agg_method = determine_aggregation(query)
    grouped_data = df.groupby(group_col)[numeric_col].agg(agg_method).reset_index()
    grouped_data = grouped_data.sort_values(numeric_col, ascending=False)

    # Solid color palette (from uploaded image)
    bar_colors = ['#4169E1', '#3CB371', '#FFA500', '#DC143C', '#DA70D6']

    # Set seaborn theme
    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=grouped_data,
        x=group_col,
        y=numeric_col,
        palette=bar_colors[:len(grouped_data)],
        ax=ax
    )

    ax.set_xlabel(group_col, fontsize=11)
    ax.set_ylabel(f"{agg_method.capitalize()} of {numeric_col}", fontsize=11)
    ax.set_title(f"{numeric_col} by {group_col} ({agg_method})", fontsize=13, pad=15)

    # Remove top and right spines
    sns.despine(ax=ax, top=True, right=True)

    # Remove y-axis ticks, gridlines
    ax.grid(False)
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('none')

    # Add labels on top of bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f', label_type='edge', fontsize=10, padding=3)

    # Rotate x-axis labels if needed
    if len(grouped_data) > 5:
        plt.xticks(rotation=45, ha='right')

    st.pyplot(fig)

    # Summary statistics
    st.write("\nSummary Statistics:")
    stats = grouped_data[numeric_col].describe()
    st.write(f"- Average {numeric_col}: {stats['mean']:.2f}")
    st.write(f"- Minimum: {stats['min']:.2f}")
    st.write(f"- Maximum: {stats['max']:.2f}")
    st.write(f"- Number of groups: {len(grouped_data)}")
