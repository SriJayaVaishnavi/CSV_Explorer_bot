import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import re

def normalize(text):
    """Remove special characters and lowercase the string."""
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def extract_columns_from_query(query: str, df_columns: list):
    """Try to extract two column names from the user query using normalization."""
    query_norm = normalize(query)
    
    # First, try exact matches with full column names
    col_matches = []
    for col in df_columns:
        col_norm = normalize(col)
        if f"{col_norm}" in query_norm:
            col_matches.append(col)
    
    # If we don't have exactly 2 matches, try word-by-word matching
    if len(col_matches) != 2:
        col_matches = []
        words = query.lower().split()
        for col in df_columns:
            col_norm = normalize(col)
            for word in words:
                word_norm = normalize(word)
                if word_norm == col_norm:
                    col_matches.append(col)
                    break
            if len(col_matches) == 2:
                break
    
    return col_matches[:2] if len(col_matches) >= 2 else []

def plot_scatter(df, query: str = ""):
    st.subheader("Scatter Plot")
    
    # Get numeric columns only
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

    if len(numeric_cols) < 2:
        st.warning("You need at least two numeric columns to generate a scatter plot.")
        return

    # Attempt to auto-select from query
    col1, col2 = None, None
    if query:
        extracted = extract_columns_from_query(query, numeric_cols)
        if len(extracted) == 2:
            col1, col2 = extracted
            st.success(f"Identified columns from query: `{col1}` vs `{col2}`")
        else:
            st.warning(f"Could not identify both columns from query: '{query}'")
            st.info(f"Available numeric columns: {', '.join(numeric_cols)}")

    # Fallback or allow user to adjust
    x_axis = st.selectbox("Select X-axis", numeric_cols, index=numeric_cols.index(col1) if col1 in numeric_cols else 0)
    y_candidates = [col for col in numeric_cols if col != x_axis]
    y_axis = st.selectbox("Select Y-axis", y_candidates, index=y_candidates.index(col2) if col2 in y_candidates else 0)

    # Plot using seaborn
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax, color="skyblue", edgecolor="black", alpha=0.7)
    ax.set_title(f"{y_axis} vs {x_axis}")
    st.pyplot(fig)
