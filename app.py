import streamlit as st
from agents import workflow

st.title("🤖 Multi-Agent AI Assistant")

task = st.text_input("Enter your software task:")

agent_choice = st.selectbox(
    "Choose agent:",
    [
        "1 - Code Generator",
        "2 - Documentation Writer",
        "3 - Test Writer",
        "4 - Full Pipeline"
    ]
)

agent_choice = agent_choice[0]

if st.button("Run AI"):

    if not task.strip():
        st.warning("Please enter a task")
    else:
        state = {
            "task": task,
            "code": "",
            "docs": ""
        }

        with st.spinner("Running agents..."):
            app_graph = workflow(agent_choice)
            out = app_graph.invoke(state)

        st.subheader("💻 Code")
        if out.get("code"):
            st.code(out["code"], language="python")
        else:
            st.write("No code generated")

        st.subheader("📄 Documentation & Tests")
        if out.get("docs"):
            st.text(out["docs"])
        else:
            st.write("No documentation/tests generated")