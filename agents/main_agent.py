from langchain_openai import ChatOpenAI
from langchain_core import prompts
from langchain.agents import create_agent

from pathlib import Path
import json 



SYSTEM_PROMPT = """


"""
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "main_agent.json"


#create config dictionary
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

#Define model - if you want to use a different import from langchain
model = ChatOpenAI(
    model=config["main_model"]["model"],
    temperature = config["main_model"]["temperature"],
    top_p = config["main_model"]["top_p"],
)

#call tools here
agent_tools = []

#build agent 
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools= agent_tools
)
