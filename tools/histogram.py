import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import re
from scipy import stats

def normalize(text):
    """Normalize text, including subscript to digit mapping."""
    if not isinstance(text, str):
        text = str(text)
    subscripts = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    text = text.translate(subscripts)
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def extract_histogram_column(query: str, df: pd.DataFrame):
    """Extract the most relevant numeric column for histogram based on query context."""
    numeric_cols = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
    if not numeric_cols:
        return None

    # Normalize query and extract words
    norm_query = normalize(query)
    query_words = set(re.findall(r'[a-zA-Z]+|\d+', norm_query))

    # Remove irrelevant histogram keywords
    distribution_keywords = {
        "distribution", "spread", "range", "frequency", "occurrence",
        "pattern", "histogram", "density", "concentration"
    }
    query_words -= distribution_keywords

    # Build normalized column map
    normalized_col_map = {normalize(col): col for col in numeric_cols}

    best_match = None
    best_score = 0

    for norm_col, original_col in normalized_col_map.items():
        score = 0

        if norm_col in norm_query:
            score += 3

        col_words = set(re.findall(r'[a-zA-Z]+|\d+', norm_col))
        matching_parts = col_words & query_words
        score += len(matching_parts) * 2

        for word in query_words:
            if word in norm_col:
                score += 1

        if score > best_score:
            best_score = score
            best_match = original_col

    return best_match

def determine_bins(data):
    """Determine optimal number of bins for the histogram."""
    n = len(data)
    if n < 2:
        return 10  # fallback
    
    iqr = stats.iqr(data)
    if iqr == 0:
        return int(np.ceil(np.log2(n) + 1))  # Sturges

    h = 2 * iqr / (n ** (1 / 3))
    data_range = data.max() - data.min()
    return int(np.ceil(data_range / h)) if h > 0 else 10

def plot_histogram(df: pd.DataFrame, query: str = ""):
    """Create a histogram with distribution analysis."""
    st.subheader("Histogram Analysis")
    
    if df.empty:
        st.warning("No data available for plotting.")
        return

    column = extract_histogram_column(query, df)

    if not column:
        numeric_cols = df.select_dtypes(include=["float64", "int64", "int32"]).columns
        if numeric_cols.empty:
            st.error("No numeric columns found in the dataset.")
            return
        column = st.selectbox("Select a numeric column to analyze:", numeric_cols)

    data = df[column].dropna()
    if data.empty:
        st.error(f"No valid data points found in column '{column}'.")
        return

    n_bins = determine_bins(data)

    # Plotting
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))
    honey_color = "#FFB300"

    sns.histplot(data, bins=n_bins, kde=True, color=honey_color, edgecolor='black', ax=ax)
    ax.set_xlabel(column)
    ax.set_ylabel('Frequency')
    ax.set_title(f'Distribution of {column}')
    st.pyplot(fig)

    # Statistics
    st.write("### Distribution Statistics:")
    stats_data = {
        "Mean": data.mean(),
        "Median": data.median(),
        "Standard Deviation": data.std(),
        "Skewness": data.skew(),
        "Kurtosis": data.kurtosis(),
        "Minimum": data.min(),
        "Maximum": data.max()
    }
    for stat, value in stats_data.items():
        st.write(f"- **{stat}**: {value:.2f}")

    # Shape interpretation
    st.write("### Distribution Shape:")
    skew = stats_data["Skewness"]
    kurt = stats_data["Kurtosis"]

    if abs(skew) < 0.5:
        st.write("- The distribution is approximately symmetric.")
    elif skew > 0:
        st.write("- The distribution is **right-skewed** (longer tail on the right).")
    else:
        st.write("- The distribution is **left-skewed** (longer tail on the left).")

    if abs(kurt) < 0.5:
        st.write("- The distribution has a **normal-like peak**.")
    elif kurt > 0:
        st.write("- The distribution has a **sharper peak** than normal (**leptokurtic**).")
    else:
        st.write("- The distribution has a **flatter peak** than normal (**platykurtic**).")
