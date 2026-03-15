import streamlit as st

st.set_page_config(page_title="Party Purse Dashboard")

st.title("Party Purse Dashboard")
st.write("This is a placeholder dashboard. Add your widgets here.")

# Example placeholder for metrics
st.metric(label="Example Metric", value=42, delta=5)

# Example placeholder for a plot
import pandas as pd
import plotly.express as px

df = pd.DataFrame({
    "x": [1, 2, 3, 4],
    "y": [10, 20, 30, 40]
})
fig = px.line(df, x="x", y="y", title="Example Plot")
st.plotly_chart(fig)