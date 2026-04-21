import streamlit as st
import pandas as pd
import os
from src.assistant.agent import InventoryAgent, SYSTEM_PROMPT
# from src.assistant.tools import tools_names and add them later


st.set_page_config(page_title="Alfred Inventory System", layout="wide")

# Initialize session variables
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Authentication ---
if not st.session_state.user_name:
    st.title("Alfred System Authentication")
    with st.form("sign_in"):
        name_input = st.text_input("Employee ID / Name:")
        if st.form_submit_button("Access System"):
            if name_input:
                # Store the name
                st.session_state.user_name = name_input
                
                # agent initialization
                st.session_state.agent_executor = InventoryAgent(tools = [], system_prompt=SYSTEM_PROMPT) # add tools names here
                
                # Load history
                history = st.session_state.agent_executor.get_session_history(name_input)
                if len(history.messages) > 0:
                    # Convert SQL history to Streamlit format
                    st.session_state.messages = [
                        {"role": "user" if msg.type == "human" else "assistant", "content": msg.content}
                        for msg in history.messages
                    ]
                    # Add a Welcome back alert
                    st.session_state.messages.append({"role": "assistant", "content": f"Welcome back, {name_input}. Just upload your CSV file and we can get started."})
                else:
                    st.session_state.messages = [{"role": "assistant", "content": f"Hello {name_input}, I'm Alfred. I'll be assisting you with your inventory needs. To get started, go ahead and upload your CSV file."}]
                
                st.rerun()
    st.stop()

# --- Main Dashboard ---

# CSV Uploader
uploaded_file = st.file_uploader("Upload Inventory CSV", type="csv")
inventory_context = "No file uploaded" # Default

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df, use_container_width=True) # Show the data on screen
    
    # Update the context for Agent
    inventory_context = df.head(50).to_string() 

    # Send a message for upload
    if "file_processed" not in st.session_state or st.session_state.get("last_uploaded") != uploaded_file.name:
        st.session_state.messages.append({"role": "assistant", "content": f"Thank you for uploading '{uploaded_file.name}'. Let me know if you have any questions about the inventory. Type **/help** for a full list of my functionalities."})
        st.session_state.file_processed = True
        st.session_state.last_uploaded = uploaded_file.name

# --- Side bar chat interface ---
with st.sidebar:
    st.title(f"{st.session_state.user_name}")
    if st.button("Log Out"):
        # Clear everything on logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.subheader("Alfred Assistant")
    
    # Chat box
    chat_container = st.container(height=500)

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
            # /help intercepter
            if prompt.lower().strip() == "/help":
                response = (
                    "I am Alfred, an AI here to assist with your inventory logistics. My current capabilities include:\n"
                    "* **Data Analysis:** Identifying stock shortages and surpluses.\n"
                    "* **Information Retrieval:** Finding specific SKUs or item details.\n"
                    "* **Error Detection:** Spotting missing values in your CSV.\n"
                    "* **General Support:** Answering questions regarding the uploaded manifest."
                )
                st.markdown(response)
            # normal processing
            else:
                response = st.session_state.agent_executor.run(
                    user_input=prompt, 
                    inventory_context=inventory_context, 
                    user_name=st.session_state.user_name
                )
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})







# to run
# add .env with you API key
# pip install -r requirements.txt
# python3 -m streamlit run app.py