# CogniSphere Multi-Tool Agent

A conversational AI agent that decides **which tool to use** for each question, runs it, and turns the result into a clear answer. It can search a company policy document, look up employee details, and do percentage calculations, and it can chain these together for multi-step questions like *"What percentage of employees are in Engineering?"*

**Live demo:** `https://multitoolagent-ojdfh6suyzzbfnp9pe9pep.streamlit.app/`

> CogniSphere Technologies is a fictional company created for learning and demonstration. The policy handbook and employee data are sample data.

---

## What it does

Ask a question in plain English and the agent picks the right tool:

| You ask | Tool the agent uses |
|---|---|
| "What are the standard working hours?" | Document search (RAG) |
| "What department is John Doe in?" | Employee lookup |
| "How many employees are in Sales?" | Department headcount |
| "What percent of 200 is 50?" | Percentage calculation |
| "What is 20% of 30?" | Percentage-of calculation |
| "What percentage of employees are in Engineering?" | Headcount **then** percentage (multi-step) |

It also remembers earlier messages in the same chat, so follow-ups like *"What's his email?"* work. Questions outside its tools get a polite "I don't know" instead of a made-up answer.

## Tools

1. **`document_search`**: Retrieval over the CogniSphere policy handbook (PDF). The document is split into chunks, embedded, and stored in a FAISS vector store. A similarity-score threshold filters out irrelevant matches so off-topic questions don't return unrelated text.
2. **`employee_lookup`**: Returns an employee's department, role, and email by name.
3. **`employee_count_by_department`**: Counts employees in a department (and the total). A count of 0 is treated as a valid answer.
4. **`percentage_calculation`**: "What percent is X of Y?"
5. **`percentage_of_calculation`**: "What is X% of Y?"

Each tool is a plain Python function wrapped with LangChain's `@tool` decorator. The **docstring is what the model reads to decide when to use it**, so docstrings are written to clearly separate similar tools.

## How it works

```
User question
     |
     v
 Agent (LLM) ---> decides which tool(s) to call
     |                      |
     |                      v
     |            Tool runs and returns a result
     |                      |
     v                      v
 LLM reads the tool result --> final answer
```

- The agent is built with LangChain's `create_agent` (runs on LangGraph).
- **Memory:** a LangGraph `InMemorySaver` checkpointer keeps conversation history per `thread_id`. The Streamlit app generates a unique `thread_id` per browser session, so different visitors never share history.
- A `recursion_limit` caps tool-calling loops so the agent can't run forever.

## Tech stack

- **LLM:** Groq API (`qwen/qwen3.8-27b`)
- **Agent framework:** LangChain + LangGraph
- **Embeddings:** Hugging Face `sentence-transformers/all-MiniLM-L6-v2` (runs locally, no API key)
- **Vector store:** FAISS
- **UI:** Streamlit
- **Language:** Python


## Run locally
pip install -r requirements.txt
add GROQ_API_KEY=your_key to a .env file
streamlit run app.py

## Deployment

Deployed on Streamlit Community Cloud. The API key is stored in the app's **Secrets** settings (`GROQ_API_KEY = "..."`) instead of a `.env` file, and the code reads it with `os.getenv`, so the same code runs locally and in the cloud.

## Example questions to try

- What are the standard working hours at CogniSphere?
- How are expenses above $500 handled?
- What department is John Doe in? Then: *What's his email?*
- What percentage of employees are in Sales?
- What is 40% of 50?
- What is Artificial Intelligence? *(should say it doesn't know; it's outside the tools)*

## Lessons learned

Real issues hit while building this, and how they were solved:

- **Irrelevant retrieval:** vector search always returns the "closest" chunks, even when nothing is relevant. Fixed by measuring similarity scores for relevant vs. irrelevant queries and setting a distance threshold between them.
- **Model deprecations:** Groq retired several models during development. Model names are now checked against the live `/models` endpoint instead of tutorials.
- **Reasoning-model problems:** one model leaked its internal reasoning into answers and looped on tool calls. Switching models and tightening the system prompt ("treat tool results as final") fixed it.
- **Hallucinated answers:** setting `temperature=0` and restricting the agent to tool-only answers kept responses grounded in the document.
- **Library API changes:** the older `AgentExecutor` pattern from the course was replaced by `create_agent` in current LangChain, so the agent was rebuilt on the new API.

## Possible improvements

- Replace the hardcoded employee dictionary with a database (SQLite or CSV)
- Add an automated evaluation script that runs a fixed list of test questions
- Show which tool the agent used for each answer in the UI
- Support uploading your own PDF for document search
