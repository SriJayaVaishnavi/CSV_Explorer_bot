import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
import seaborn as sns  # Add this at the top


def normalize(text):
    """Normalize text, including subscript to digit mapping."""
    if not isinstance(text, str):
        text = str(text)
    subscripts = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    text = text.translate(subscripts)
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def extract_numeric_column(query: str, df: pd.DataFrame):
    """Extract numeric column by comparing normalized tokens to normalized column names."""
    numeric_cols = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
    if not numeric_cols:
        return None

    def normalize_token(token):
        subscripts = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
        token = token.translate(subscripts)
        return re.sub(r'[^a-zA-Z0-9]', '', token.lower())

    # Normalize individual tokens from the query
    query_tokens = query.lower().split()
    norm_query_tokens = [normalize_token(token) for token in query_tokens]

    best_match = None
    best_score = 0

    for col in numeric_cols:
        score = 0
        norm_col = normalize_token(col)

        # Score exact token match
        if norm_col in norm_query_tokens:
            score += 3

        # Score partial matches
        for token in norm_query_tokens:
            if token in norm_col:
                score += 2
            elif norm_col in token:
                score += 1

        # Update best match
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
    
    # Common grouping patterns in natural language
    grouping_patterns = [
        # Format: (keyword, score)
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
    
    # Common categorical column types
    category_indicators = [
        # Format: (keyword, score)
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
        
        # Check for explicit grouping patterns
        for pattern, pattern_score in grouping_patterns:
            if pattern in query_lower:
                after_pattern = query_lower.split(pattern)[-1].strip()
                if normalize(col) in normalize(after_pattern):
                    score += pattern_score * 2
                    
        # Check if column name contains category indicators
        for indicator, indicator_score in category_indicators:
            if indicator in col_lower:
                score += indicator_score
                
        # Check for direct mention in query
        if normalize(col) in norm_query:
            score += 3
            
        # Check for column parts in query
        col_parts = set(word.strip() for word in col_lower.split())
        query_parts = set(word.strip() for word in query_lower.split())
        matching_parts = col_parts.intersection(query_parts)
        score += len(matching_parts)
        
        # Update best match if we found a better score
        if score > best_score:
            best_score = score
            best_match = col
            
    return best_match

def determine_aggregation(query: str):
    """Determine the aggregation method from query context."""
    query = query.lower()
    
    # Aggregation patterns with examples
    aggregations = {
        "mean": ["average", "mean", "avg", "typical", "expected"],
        "sum": ["total", "sum", "overall", "combined", "aggregate"],
        "count": ["count", "number of", "frequency", "occurrences", "instances"],
        "max": ["maximum", "max", "highest", "peak", "greatest", "top"],
        "min": ["minimum", "min", "lowest", "bottom", "least"],
        "median": ["median", "middle", "mid", "50th percentile"],
        "std": ["standard deviation", "std", "variation", "spread", "dispersion"]
    }
    
    # Score each aggregation method
    scores = {method: 0 for method in aggregations}
    
    for method, keywords in aggregations.items():
        for keyword in keywords:
            if keyword in query:
                scores[method] += 1
                # Give extra weight to exact matches
                if f" {keyword} " in f" {query} ":
                    scores[method] += 1
                    
    # Get the method with highest score
    best_method = max(scores.items(), key=lambda x: x[1])[0]
    
    # Default to mean if no clear winner
    return best_method if scores[best_method] > 0 else "mean"

def plot_bar(df: pd.DataFrame, query: str = ""):
    """Create a bar chart based on the query using seaborn."""
    st.subheader("Bar Chart")
    
    if df.empty:
        st.warning("No data available for plotting.")
        return
        
    # Extract columns from query
    numeric_col = extract_numeric_column(query, df)
    group_col = extract_categorical_column(query, df)
    
    # Let user select columns if not found in query
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
    
    # Determine aggregation method
    agg_method = determine_aggregation(query)
    
    # Group and aggregate the data
    grouped_data = df.groupby(group_col)[numeric_col].agg(agg_method).reset_index()
    
    # Sort values for better visualization
    grouped_data = grouped_data.sort_values(numeric_col, ascending=False)
    
    # Create the seaborn bar plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=grouped_data, x=group_col, y=numeric_col, palette='Set2', ax=ax)
    
    # Customize the plot
    ax.set_xlabel(group_col)
    ax.set_ylabel(f"{agg_method.capitalize()} of {numeric_col}")
    ax.set_title(f"{numeric_col} by {group_col} ({agg_method})")
    
    # Rotate x-axis labels if there are many categories
    if len(grouped_data) > 5:
        plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', label_type='edge', padding=3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Display the plot
    st.pyplot(fig)
    
    # Show summary statistics
    st.write("\nSummary Statistics:")
    stats = grouped_data[numeric_col].describe()
    st.write(f"- Average {numeric_col}: {stats['mean']:.2f}")
    st.write(f"- Minimum: {stats['min']:.2f}")
    st.write(f"- Maximum: {stats['max']:.2f}")
    st.write(f"- Number of groups: {len(grouped_data)}")
