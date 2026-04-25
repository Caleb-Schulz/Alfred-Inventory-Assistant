# app.py
import pandas as pd
import streamlit as st
from src.assistant.agent import InventoryAgent, SYSTEM_PROMPT
from src.tools.inventory_restock_tool import inventory_restock_tool
from src.data_processing.parser import read_inventory_csv
from src.data_modification.data_modify import add_data_to_column

st.set_page_config(page_title="Alfred Inventory System", layout="wide")

# Initialize session variables
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize dfs
if "original_df" not in st.session_state:
    st.session_state.original_df = None
if "current_df" not in st.session_state:
    st.session_state.current_df = None

# --- Authentication ---
if not st.session_state.user_name:
    st.title("Alfred System Authentication")
    with st.form("sign_in"):
        name_input = st.text_input("Employee ID / Name:")
        if st.form_submit_button("Access System"):
            if name_input:
                st.session_state.user_name = name_input

                st.session_state.agent_executor = InventoryAgent(
                    tools=[inventory_restock_tool, add_data_to_column],
                    system_prompt=SYSTEM_PROMPT
                )

                # Load history
                history = st.session_state.agent_executor.get_session_history(name_input)
                if len(history.messages) > 0:
                    # Convert SQL history to Streamlit format
                    st.session_state.messages = [
                        {"role": "user" if msg.type == "human" else "assistant", "content": msg.content}
                        for msg in history.messages
                    ]
                    # Add a Welcome back alert
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Welcome back, {name_input}. Just upload your CSV file and we can get started."
                    })
                else:
                    st.session_state.messages = [{
                        "role": "assistant",
                        "content": f"Hello {name_input}, I'm Alfred. I'll be assisting you with your inventory needs. To get started, go ahead and upload your CSV file."
                    }]

                st.rerun()
    st.stop()

# --- Main Dashboard ---

# CSV Uploader
uploaded_file = st.file_uploader("Upload Inventory CSV", type="csv")
inventory_context = "No file uploaded"

if uploaded_file:
    # checks if new file
    is_new_file = st.session_state.get("last_uploaded") != uploaded_file.name
    df, summary = read_inventory_csv(uploaded_file)

    if is_new_file:
        st.session_state.original_df = df.copy()
        st.session_state.current_df = df.copy()
        st.session_state.last_uploaded = uploaded_file.name

        # new file Upload Message
        upload_msg = f"Thank you for uploading '{uploaded_file.name}'. Let me know if you have any questions about the inventory. Type **/help** for a full list of my functionalities."
        st.session_state.messages.append({"role": "assistant", "content": upload_msg})

    # st.write("Summary:", summary)

    # allows agent to see table
    inventory_context = st.session_state.current_df.to_csv(index=False)
    st.session_state.inventory_json = st.session_state.current_df.to_json(orient="records")

    # --- Display Tables ---
    
    # 1. Display original Data only if diffrent
    if st.session_state.original_df is not None and not st.session_state.original_df.equals(st.session_state.current_df):
        st.subheader("Original Inventory Manifest (Reference)")
        st.dataframe(st.session_state.original_df, width="stretch")
        st.divider()

    # 2. Display Current Data
    st.subheader("Current Inventory Manifest")
    st.dataframe(st.session_state.current_df, width="stretch")

    # --- EXPORT SECTION ---
    # Convert dataframe to CSV for downloading
    csv_data = st.session_state.current_df.to_csv(index=False).encode("utf-8")
    
    btn = st.download_button(
        label="Export Current Inventory to CSV",
        data=csv_data,
        file_name=f"alfred_exported_{uploaded_file.name}",
        mime="text/csv",
    )

    # send export massage
    if btn:
        export_msg = "Export successful, Thank you for using Alfred inventory assistant. Let me know if there is anything else I can help you with."
        st.session_state.messages.append({"role": "assistant", "content": export_msg})
        st.rerun()

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
                    "* **Restock Analysis:** Flags SAFE, LOW, URGENT, and UNKNOWN items and calculates reorder quantities.\n"
                    "* **Data Modification:** Updates missing or incorrect inventory values when requested.\n"
                    "* **General Support:** Answering questions regarding the uploaded manifest."
                )
                st.markdown(response)
            # normal processing
            else:
                try: 
                    agent_result = st.session_state.agent_executor.run(
                        user_input=prompt,
                        inventory_context=inventory_context,
                        inventory_json=st.session_state.get("inventory_json", "[]"),
                        user_name=st.session_state.user_name
                    )

                    response = agent_result["output"]

                    if "intermediate_steps" in agent_result:
                        for step in agent_result["intermediate_steps"]:
                            action, observation = step

                            if isinstance(observation, dict) and observation.get("unit") == "inventory_update":
                                updated_json = observation.get("result")

                                if updated_json:
                                    st.session_state.inventory_json = updated_json
                                    st.session_state.current_df = pd.read_json(updated_json, orient="records")
                                    inventory_context = st.session_state.current_df.head(50).to_string()
                                    st.rerun()

                    st.markdown(response)
                except Exception as e:
                    # 2. Handle the 429 Quota error gracefully
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        response = "**Rate Limit Reached:** I'm on the free tier and need a quick breather (about 60 seconds). Please try your request again in a moment!"
                    else:
                        response = f"I encountered an unexpected error: {str(e)}"
                    
                    st.error(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


# to run
# add .env with you API key
# pip install -r requirements.txt
# python3 -m streamlit run app.py