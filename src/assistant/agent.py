# agent.py
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Try to load local .env
load_dotenv()

# Get key from environment OR streamlit secrets
# Will put API key in Streamlit "Secrets" for deployment
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("No API Key found. Please configure the environment.")

SYSTEM_PROMPT = f"""
You are Alfred, an expert Supply Chain & Inventory Specialist.
Your role is to act as a knowledgeable partner who combines deep data analysis with helpful, contextual conversation.

== CORE DIRECTIVE ==
While your expertise is inventory, you are a conversational AI. You should use your memory of the current session to provide continuity. If a user asks a general question or follows up on a previous point, answer helpfully while keeping the context of their inventory in mind.

== OPERATIONAL GUIDELINES ==
1. Intelligent Memory: Actively reference the 'PREVIOUS CONVERSATION' context. If the user refers to "it," "that," or "the last one," use the history to identify what they mean.
2. Data Grounding: Always use the 'FULL INVENTORY DATA' provided to ensure your facts are accurate. If the data is missing, admit it rather than guessing.
3. Professional but Personable: Maintain a grounded, expert-level demeanor, but be conversational. You are a colleague, not a rigid script.
4. Tool Usage: Use your tools for math and flagging, but use your internal knowledge to explain the *implications* of that data.
5. Response Format: Provide your final response using the 'Final Answer:' prefix as required by the ReAct framework.
== FUNCTIONALITIES ==
Data Analysis: Identifying stock shortages and surpluses.
Information Retrieval: Finding specific SKUs or item details.
Error Detection: Spotting missing values in your CSV.
Restock Analysis: Flags SAFE, LOW, URGENT, and UNKNOWN items and calculates reorder quantities.
Data Modification: Updating missing or incorrect inventory values when the user requests a correction.
When updating inventory data, use the data modification tool with a single instruction like: set row 0 supplier to FreshCo.
General Support: Answering questions regarding the uploaded manifest.

== RESTOCKING GUIDELINES ==
When a user asks about restocking:
1. Run the inventory_restock_tool ONCE.
2. Look at the 'detail' summary and the 'status' column in the result.
3. Immediately summarize the findings for the user. 
4. DO NOT call the tool multiple times for the same request.
5. If the tool returns 'URGENT' or 'LOW' items, list them clearly.
"""

class InventoryAgent:
    def __init__(self, tools, system_prompt):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,  # Lower temperature for precision over probability 
            google_api_key=api_key
        )
        self.tools = tools
        self.system_prompt = system_prompt
        
        base_prompt = hub.pull("hwchase17/react")

        # adds system prompt to initializeion
        custom_template = f"{self.system_prompt}\n\n" + base_prompt.template
        base_prompt.template = custom_template
        
        self.prompt = base_prompt
        
        # Initialize the agent
        self.agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True, 
            handle_parsing_errors=True,
            max_iterations=3,           # STOP after 3 tries to prevent a loop
            return_intermediate_steps=True
        )

    def get_session_history(self, session_id: str):
        # This creates a local database file (memory.db) to store chat logs.
        return SQLChatMessageHistory(
            session_id=session_id, 
            connection_string="sqlite:///data/memory.db"
        )

    def run(self, user_input, inventory_context, inventory_json, user_name):
        # missing user name safty net
        if not user_name or user_name.strip() == "":
            user_name = "Guest_User"

        # Pulls previous messages from the database
        history = self.get_session_history(user_name)
        chat_history = history.messages

        # Check if context exists
        if not inventory_context:
            inventory_context = "No inventory file has been uploaded yet. Please ask the user to upload a CSV."

        # Check if inventory JSON exists
        if not inventory_json:
            inventory_json = "[]"
        
        #It will only remember the last 10 lines
        formatted_history = "\n".join([f"{msg.type}: {msg.content}" for msg in chat_history[-10:]])

        # Formats the input with the history and current data
        full_input = (
            f"PREVIOUS CONVERSATION:\n{formatted_history}\n\n" 
            f"FULL INVENTORY DATA (CSV Format):\n{inventory_context}\n\n"
            f"USER REQUEST: {user_input}"
        )
    
        # Execute and Save the result to the database
        result = self.executor.invoke({"input": full_input})

        history.add_user_message(user_input)

        output_text = result["output"]
        if not isinstance(output_text, str):
            output_text = str(output_text)

        history.add_ai_message(output_text)
        result["output"] = output_text

        return result