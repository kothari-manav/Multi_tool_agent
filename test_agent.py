
"""from tools.percentage_tool import percentage_calculation

result = percentage_calculation.invoke({"part": 100, "whole": 200})
print(result)
#####
from tools.document_tool import document_search

result=document_search.invoke({"query":"What is Artificial Intelligence"})
print(result)

from tools.employee_tool import employee_lookup

result = employee_lookup.invoke({"name": "John Doe"})
print(result)

result2 = employee_lookup.invoke({"name": "Random Person"})
print(result2)
"""

"""from agent import agent
config={"configurable":{"thread_id":"user_1"}}
response1 = agent.invoke({"messages": [{"role": "user", "content": "What department is John Doe in?"}]}, config)
print(response1["messages"][-1].content)

response2 = agent.invoke({"messages": [{"role": "user", "content": "What's his email?"}]}, config)
print(response2["messages"][-1].content)

config_user2 = {"configurable": {"thread_id": "user-2"}}  # different thread_id

response = agent.invoke({"messages": [{"role": "user", "content": "What's his email?"}]}, config_user2)
print(response["messages"][-1].content)

from tools.document_tool import vectorstore

for q in [
    "expenses above $500",
    "how are expenses handled",
    "What are the working hours?",
]:
    print("QUERY:", q)
    for doc, score in vectorstore.similarity_search_with_score(q, k=5):
        print(f"  {score:.4f} | {doc.page_content[:70]!r}")
    print("-----")
"""

