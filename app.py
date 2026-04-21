import streamlit as st
import pandas as pd
import os
from src.assistant.agent import InventoryAgent, SYSTEM_PROMPT
# from src.assistant.tools import tools_names

st.set_page_config(page_title="Alfred Inventory System", layout="wide")

# Sign in screen for agent memory
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.user_name:
    st.title("Alfred System Authentication")
    with st.form("sign_in"):
        name_input = st.text_input("Employee ID / Name:")
        if st.form_submit_button("Access System"):
            if name_input:
                st.session_state.user_name = name_input
                st.rerun()
    st.stop()

# agent initialization
    if "agent_executor" not in st.session_state:
        tools_list = [] # enter tools
        st.session_state.agent_executor = InventoryAgent(tools=tools_list, system_prompt=SYSTEM_PROMPT)

# Right side bar chat interface
with st.sidebar:
    st.title(f"{st.session_state.user_name}")
    if st.button("Log Out"):
        st.session_state.user_name = ""
        st.rerun()
    
    st.divider()
    st.subheader("Alfred Assistant")
    
    # Chat box
    chat_container = st.container(height=400)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for msg in st.session_state.messages:
        with chat_container.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Text box
    if prompt := st.chat_input("Ask Alfred..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        with chat_container.chat_message("assistant"):
            response = st.session_state.agent_executor.run(
                user_input=prompt, 
                inventory_context=inventory_context, 
                user_name=st.session_state.user_name
            )
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})







# to run
# pip install -r requirements.txt
# streamlit run app.py