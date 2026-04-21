import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Load security environment variables
load_dotenv()

SYSTEM_PROMPT = f"""
You are a professional supply chain and inventory specialist named "Alfred".
Your goal is to assist in the precision management of inventory through deterministic data analysis.

== OPERATIONAL GUIDELINES ==
1. Precision over Probability: When asked for calculations, sorting, or flagging, use your provided tools rather than estimating.
2. Contextual Awareness: You have access to a live inventory dataframe. Always reference current stock levels before suggesting actions.
3. Concise Communication: Keep answers concise (2-4 sentences) unless a detailed report or data table is requested.
4. Professional Tone: Maintain a grounded, expert-level demeanor suitable for an enterprise environment.

== MEMORY & DATA PERSISTENCE ==
1. Historical Context: You must remember previous user instructions (e.g., if the user previously asked to "flag shortages," maintain that context in the current turn).
2. Data Synchronization: Every response must be grounded in the most recent version of the inventory dataframe provided in the context.
3. Change Tracking: If a tool was used to modify the list in a previous turn, acknowledge that change when answering follow-up questions.
"""

class InventoryAgent:
    def __init__(self, tools, system_prompt):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,  # Lower temperature for precision over probability 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.tools = tools
        self.system_prompt = system_prompt
        self.prompt = hub.pull("hwchase17/react")
        
        # Initialize the agent
        self.agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True, 
            handle_parsing_errors=True
        )
    def get_session_history(self, session_id: str):
        # This creates a local database file (memory.db) to store chat logs.
        return SQLChatMessageHistory(
            session_id=session_id, 
            connection_string="sqlite:///data/memory.db"
        )

    def run(self, user_input, inventory_context, user_name):
        # missing user name safty net
        if not user_name or user_name.strip() == "":
            user_name = "Guest_User"

        # Pulls previous messages from the database
        history = self.get_session_history(user_name)
        chat_history = history.messages

        # Check if context exists
        if not inventory_context:
            inventory_context = "No inventory file has been uploaded yet. Please ask the user to upload a CSV."
        
        #It will only remember the last 10 lines
        formatted_history = "\n".join([f"{msg.type}: {msg.content}" for msg in chat_history[-10:]])

        # Formats the input with the history and current data
        full_input = (
            f"{self.system_prompt}\n\n"
            f"PREVIOUS CONVERSATION:\n{formatted_history}\n\n" 
            f"CURRENT INVENTORY:\n{inventory_context}\n\n"
            f"USER REQUEST: {user_input}"
        )
    
        # Execute and Save the result to the database
        result = self.executor.invoke({"input": full_input})
        
        history.add_user_message(user_input)
        history.add_ai_message(result["output"])
        
        return result["output"]