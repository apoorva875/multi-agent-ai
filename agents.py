import os
from langgraph.graph import StateGraph, START
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from typing import TypedDict, Dict
from dotenv import load_dotenv
load_dotenv()

# ✅ LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.5,
    max_tokens=500
)

# ✅ State
class State(TypedDict):
    task: str
    code: str
    docs: str

# ✅ Code Agent
class CodeGenerator:
    def generate_code(self, state: State) -> Dict:
        prompt = f"""
        Write ONLY Python code for the task below.
        Do NOT include explanations.

        Task: {state['task']}
        """
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"code": response.content}

# ✅ Docs Agent
class DocumentationWriter:
    def write_documentation(self, state: State) -> Dict:
        if not state.get("code"):
            return {"docs": "No code available for documentation."}

        prompt = f"Write short documentation for:\n{state['code']}"
        response = llm.invoke([HumanMessage(content=prompt)])

        return {"docs": response.content}

# ✅ Test Agent
class TestWriter:
    def write_tests(self, state: State) -> Dict:
        if not state.get("code"):
            return {"docs": state.get("docs", "") + "\n\nNo code available for tests."}

        prompt = f"Write unit tests for:\n{state['code']}"
        response = llm.invoke([HumanMessage(content=prompt)])

        return {
            "docs": state.get("docs", "") + "\n\nTESTS:\n" + response.content
        }

# ✅ Workflow
def workflow(agent_name: str):
    g = StateGraph(State)

    if agent_name not in ["1", "2", "3", "4"]:
        agent_name = "4"

    code_agent = CodeGenerator()
    doc_agent = DocumentationWriter()
    test_agent = TestWriter()

    if agent_name == "1":
        g.add_node("generate_code", code_agent.generate_code)
        g.add_edge(START, "generate_code")

    elif agent_name == "2":
        g.add_node("write_documentation", doc_agent.write_documentation)
        g.add_edge(START, "write_documentation")

    elif agent_name == "3":
        g.add_node("write_tests", test_agent.write_tests)
        g.add_edge(START, "write_tests")

    elif agent_name == "4":
        g.add_node("generate_code", code_agent.generate_code)
        g.add_node("write_documentation", doc_agent.write_documentation)
        g.add_node("write_tests", test_agent.write_tests)

        g.add_edge(START, "generate_code")

        # ✅ SEQUENTIAL (fixes missing output issue)
        g.add_edge("generate_code", "write_documentation")
        g.add_edge("write_documentation", "write_tests")

    return g.compile()