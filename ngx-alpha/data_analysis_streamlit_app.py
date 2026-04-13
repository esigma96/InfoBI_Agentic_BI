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
