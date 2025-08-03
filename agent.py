import os, uuid
from langgraph.prebuilt import create_react_agent
from langmem          import create_manage_memory_tool, create_search_memory_tool
from markdown_store   import MarkdownStore

STORE = MarkdownStore(base_path="kg")

agent = create_react_agent(
    model="openai:gpt-4.1-mini",
    tools=[
        create_manage_memory_tool(namespace=("mem",), store=STORE),
        create_search_memory_tool(namespace=("mem",),  store=STORE),
    ],
)

if __name__ == "__main__":
    uid = os.environ.get("USER", "local")
    while True:
        try:
            user = input("👤  > ")
        except (EOFError, KeyboardInterrupt):
            break
        rsp = agent.invoke(user, config={"configurable": {"user_id": uid}})
        print("🤖 ", rsp)
