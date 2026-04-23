# The Python "Non-LLM" tools
# This is where you put tools for the agent to use

# if you add a tool here you must
# add the name to the app.py import, agent initialization, and /help


from langchain.tools import tool
import pandas as pd

# @tool