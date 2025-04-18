# Summary tool
import streamlit as st

def show_summary(df,query):
    print("entered show summary")
    st.subheader("DataFrame Summary")
    st.write("**Shape of the DataFrame:**", df.shape)
    st.write("**Data Types:**")
    st.write(df.dtypes)
    st.write("**Summary Statistics:**")
    st.write(df.describe())
    st.write("**Missing Values:**")
    st.write(df.isnull().sum())
