import streamlit as st
import pandas as pd
import os
import json
import pickle

from langchain_core.messages import HumanMessage, AIMessage
from Pages.backend import PythonChatbot
from Pages.data_models import InputData


# -----------------------------
# PATH SETUP (SAFE FOR CLOUD)
# -----------------------------
BASE_DIR = os.path.dirname(__file__)

UPLOAD_DIR = os.path.join(BASE_DIR, "..", "uploads")
DATA_DICT_PATH = os.path.join(BASE_DIR, "..", "data_dictionary.json")
IMAGE_DIR = os.path.join(BASE_DIR, "..", "images/plotly_figures/pickle")

os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("Agentic BI - InfoBI")


# -----------------------------
# LOAD DATA DICTIONARY
# -----------------------------
with open(DATA_DICT_PATH, "r") as f:
    data_dictionary = json.load(f)


# -----------------------------
# SESSION STATE INIT (CRITICAL FIX)
# -----------------------------
if "visualisation_chatbot" not in st.session_state:
    st.session_state.visualisation_chatbot = PythonChatbot()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "output_image_paths" not in st.session_state:
    st.session_state.output_image_paths = {}

if "intermediate_outputs" not in st.session_state:
    st.session_state.intermediate_outputs = []

if "selected_files" not in st.session_state:
    st.session_state.selected_files = []


# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs(["Data Management", "Chat Interface", "Debug"])


# =============================
# TAB 1 - DATA MANAGEMENT
# =============================
with tab1:

    uploaded_files = st.file_uploader(
        "Upload CSV files",
        type="csv",
        accept_multiple_files=True
    )

    if uploaded_files:
        for file in uploaded_files:
            with open(os.path.join(UPLOAD_DIR, file.name), "wb") as f:
                f.write(file.getbuffer())
        st.success("Files uploaded successfully!")

    available_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".csv")]

    if available_files:

        st.session_state.selected_files = st.multiselect(
            "Select files to analyze",
            available_files,
            key="selected_files_ui"
        )

        new_descriptions = {}

        if st.session_state.selected_files:

            file_tabs = st.tabs(st.session_state.selected_files)

            for tab, filename in zip(file_tabs, st.session_state.selected_files):

                with tab:
                    df = pd.read_csv(os.path.join(UPLOAD_DIR, filename))
                    st.dataframe(df.head())

                    st.subheader("Dataset Information")

                    current_desc = data_dictionary.get(filename, {}).get("description", "")

                    new_descriptions[filename] = st.text_area(
                        "Dataset Description",
                        value=current_desc,
                        key=f"desc_{filename}"
                    )

        if st.button("Save Descriptions"):

            for filename, description in new_descriptions.items():
                if filename not in data_dictionary:
                    data_dictionary[filename] = {}

                data_dictionary[filename]["description"] = description

            with open(DATA_DICT_PATH, "w") as f:
                json.dump(data_dictionary, f, indent=4)

            st.success("Saved successfully!")

    else:
        st.info("No CSV files available. Upload some files first.")


# =============================
# TAB 2 - CHAT INTERFACE
# =============================
with tab2:

    # -----------------------------
    # SAFE CHAT FUNCTION
    # -----------------------------
    def on_submit_user_query():

        user_query = st.session_state.get("user_input", "")

        input_data_list = [
            InputData(
                variable_name=file.split(".")[0],
                data_path=os.path.abspath(os.path.join(UPLOAD_DIR, file)),
                data_description=data_dictionary.get(file, {}).get("description", "")
            )
            for file in st.session_state.selected_files
        ]

        result = st.session_state.visualisation_chatbot.run({
            "query": user_query,
            "input_data": input_data_list
        })

        # STORE RESULT IN STREAMLIT STATE (IMPORTANT FIX)
        st.session_state.chat_history = result.get("chat_history", [])
        st.session_state.output_image_paths = result.get("output_image_paths", {})
        st.session_state.intermediate_outputs = result.get("intermediate_outputs", [])


    # -----------------------------
    # MAIN CHAT UI
    # -----------------------------
    if st.session_state.selected_files:

        chat_container = st.container(height=500)

        with chat_container:

            for msg_index, msg in enumerate(st.session_state.chat_history):

                msg_col, img_col = st.columns([2, 1])

                with msg_col:

                    if isinstance(msg, HumanMessage):
                        st.chat_message("You").markdown(msg.content)

                    elif isinstance(msg, AIMessage):
                        with st.chat_message("AI"):
                            st.markdown(msg.content)

                    if (
                        isinstance(msg, AIMessage)
                        and msg_index in st.session_state.output_image_paths
                    ):
                        for image_path in st.session_state.output_image_paths[msg_index]:

                            fig_path = os.path.join(IMAGE_DIR, image_path)

                            with open(fig_path, "rb") as f:
                                fig = pickle.load(f)

                            st.plotly_chart(fig, use_container_width=True)


        # CHAT INPUT (FIXED)
        st.text_input(
            "Ask me anything about your data",
            key="user_input",
            on_change=on_submit_user_query
        )

    else:
        st.info("Please select files in Data Management tab first.")


# =============================
# TAB 3 - DEBUG
# =============================
with tab3:

    st.subheader("Intermediate Outputs")

    if st.session_state.intermediate_outputs:

        for i, output in enumerate(st.session_state.intermediate_outputs):

            with st.expander(f"Step {i+1}"):

                if isinstance(output, dict):
                    if "thought" in output:
                        st.markdown("### Thought Process")
                        st.markdown(output["thought"])

                    if "code" in output:
                        st.markdown("### Code")
                        st.code(output["code"], language="python")

                    if "output" in output:
                        st.markdown("### Output")
                        st.text(output["output"])

                else:
                    st.text(output)

    else:
        st.info("No debug information available yet.")
