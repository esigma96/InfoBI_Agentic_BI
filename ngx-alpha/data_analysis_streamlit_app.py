import os
os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "2000"
os.environ["OPENAI_API_KEY"] = "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"
import streamlit as st

# Set Streamlit to wide mode
st.set_page_config(layout="wide", page_title="Main Dashboard", page_icon="📊")


data_visualisation_page = st.Page(
    "./Pages/python_visualisation_agent.py", title="Data Visualisation", icon="📈"
)

pg = st.navigation(
    {
        "Visualisation Agent": [data_visualisation_page]
    }
)

pg.run()
