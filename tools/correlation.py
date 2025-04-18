# Correlation matrix tool
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

def plot_correlation(df, query=None):
    st.subheader("Correlation Matrix")
    
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=['number'])
    
    if numeric_df.empty:
        st.warning("No numeric columns found in the dataset.")
        return
    
    if len(numeric_df.columns) < 2:
        st.warning("Need at least 2 numeric columns to create a correlation matrix.")
        return
    
    # Create correlation matrix
    corr_matrix = numeric_df.corr()
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, 
                annot=True,           # Show correlation values
                fmt='.2f',           # Format to 2 decimal places
                cmap='coolwarm',     # Color scheme
                center=0,            # Center the colormap at 0
                square=True,         # Make cells square
                ax=ax)
    
    plt.title("Correlation Matrix of Numeric Variables")
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # Add correlation interpretation
    st.markdown("""
    ### Interpretation:
    - Values close to 1 indicate strong positive correlation
    - Values close to -1 indicate strong negative correlation
    - Values close to 0 indicate little to no correlation
    """)
    
    # Find and display strongest correlations
    correlations = corr_matrix.unstack()
    sorted_correlations = correlations[correlations != 1.0].abs().sort_values(ascending=False)
    
    if not sorted_correlations.empty:
        st.subheader("Strongest Correlations:")
        for idx, value in sorted_correlations[:5].items():
            var1, var2 = idx
            if var1 != var2:
                st.write(f"- {var1} vs {var2}: {corr_matrix.loc[var1, var2]:.2f}")
