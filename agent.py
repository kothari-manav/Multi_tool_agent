from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from tools.percentage_tool import percentage_calculation
from tools.employee_tool import employee_lookup
from tools.document_tool import document_search
from tools.employee_tool import employee_count_by_department

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")

llm=ChatGroq(model="openai/gpt-oss-120b", groq_api_key=GROQ_API_KEY,temperature=0)
tools=[percentage_calculation,document_search,employee_lookup,employee_count_by_department]

checkpointer=InMemorySaver()
agent = create_agent(
    llm,
    tools,
system_prompt=(
    "You are a company assistant for CogniSphere Technologies. "
    "You must ONLY answer using information from your available tools. "
    "For questions requiring multiple steps (e.g. 'what percentage of employees are in X'), "
    "always complete ALL required tool calls before answering — first get the count, "
    "then calculate the percentage. Do not stop early. "
    "Only respond with 'I don't know, that's outside what I can help with' if NONE "
    "of your tools can answer the question at all — never for questions your tools "
    "CAN answer, even if the result is a small number like 0 or 1."
),
    checkpointer=checkpointer,
)
"""
It was used for test one by one tools but not neccesary after testing as we are going to ask in UI
def ask_question(question):
    response=agent.invoke({"messages":[{"role":"user","content":question}]})
    print(response["messages"][-1].content)

ask_question("What percentage of employees are in Engineering?")"""