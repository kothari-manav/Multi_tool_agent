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

llm=ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=GROQ_API_KEY,temperature=0,reasoning_format="hidden")
tools=[percentage_calculation,document_search,employee_lookup,employee_count_by_department]

checkpointer=InMemorySaver()
agent = create_agent(
    llm,
    tools,
system_prompt=(
    "You are a company assistant for CogniSphere Technologies. "
    "Answer ONLY using your tools (document search, employee lookup, "
    "employee count, percentage calculations). Do not use general knowledge. "
    "For multi-step questions like 'what percentage of employees are in X', "
    "first get the count, then calculate the percentage. "
    "Treat every tool result as final: do not call the same tool again with a "
    "reworded query. A result like '0 out of 3' or 'No relevant information found' "
    "is a complete answer, so report it directly. "
    "If none of your tools can answer the question, reply exactly: "
    "'I don't know, that's outside what I can help with.'"
),
    checkpointer=checkpointer,
)

"""
It was used for test one by one tools but not neccesary after testing as we are going to ask in UI
def ask_question(question):
    response=agent.invoke({"messages":[{"role":"user","content":question}]})
    print(response["messages"][-1].content)

ask_question("What percentage of employees are in Engineering?")"""