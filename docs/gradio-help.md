A real example using langchain agents

We'll create a UI for langchain agent that has access to a search engine.

We'll begin with imports and setting up the langchain agent. Note that you'll need an .env file with the following environment variables set -


SERPAPI_API_KEY=
HF_TOKEN=
OPENAI_API_KEY=

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent, load_tools
from langchain_openai import ChatOpenAI
from gradio import ChatMessage
import gradio as gr

from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(temperature=0, streaming=True)

tools = load_tools(["serpapi"])

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-tools-agent")
agent = create_openai_tools_agent(
    model.with_config({"tags": ["agent_llm"]}), tools, prompt
)
agent_executor = AgentExecutor(agent=agent, tools=tools).with_config(
    {"run_name": "Agent"}
)
Then we'll create the Gradio UI


async def interact_with_langchain_agent(prompt, messages):
    messages.append(ChatMessage(role="user", content=prompt))
    yield messages
    async for chunk in agent_executor.astream(
        {"input": prompt}
    ):
        if "steps" in chunk:
            for step in chunk["steps"]:
                messages.append(ChatMessage(role="assistant", content=step.action.log,
                                  metadata={"title": f"🛠️ Used tool {step.action.tool}"}))
                yield messages
        if "output" in chunk:
            messages.append(ChatMessage(role="assistant", content=chunk["output"]))
            yield messages


with gr.Blocks() as demo:
    gr.Markdown("# Chat with a LangChain Agent 🦜⛓️ and see its thoughts 💭")
    chatbot = gr.Chatbot(
        type="messages",
        label="Agent",
        avatar_images=(
            None,
            "https://em-content.zobj.net/source/twitter/141/parrot_1f99c.png",
        ),
    )
    input = gr.Textbox(lines=1, label="Chat Message")
    input.submit(interact_with_langchain_agent, [input_2, chatbot_2], [chatbot_2])

demo.launch()


The ChatMessage dataclass

Each message in Gradio's chatbot is a dataclass of type ChatMessage (this is assuming that chatbot's type="message", which is strongly recommended). The schema of ChatMessage is as follows:


@dataclass
class ChatMessage:
   content: str | Component
   role: Literal["user", "assistant"]
   metadata: MetadataDict = None
   options: list[OptionDict] = None

class MetadataDict(TypedDict):
   title: NotRequired[str]
   id: NotRequired[int | str]
   parent_id: NotRequired[int | str]
   log: NotRequired[str]
   duration: NotRequired[float]
   status: NotRequired[Literal["pending", "done"]]

class OptionDict(TypedDict):
   label: NotRequired[str]
   value: str
For our purposes, the most important key is the metadata key, which accepts a dictionary. If this dictionary includes a title for the message, it will be displayed in a collapsible accordion representing a thought. It's that simple! Take a look at this example:


import gradio as gr

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        type="messages",
        value=[
            gr.ChatMessage(
                role="user", 
                content="What is the weather in San Francisco?"
            ),
            gr.ChatMessage(
                role="assistant", 
                content="I need to use the weather API tool?",
                metadata={"title":  "🧠 Thinking"}
        ]
    )

demo.launch()
In addition to title, the dictionary provided to metadata can take several optional keys:

log: an optional string value to be displayed in a subdued font next to the thought title.
duration: an optional numeric value representing the duration of the thought/tool usage, in seconds. Displayed in a subdued font next inside parentheses next to the thought title.
status: if set to "pending", a spinner appears next to the thought title and the accordion is initialized open. If status is "done", the thought accordion is initialized closed. If status is not provided, the thought accordion is initialized open and no spinner is displayed.
id and parent_id: if these are provided, they can be used to nest thoughts inside other thoughts.
Below, we show several complete examples of using gr.Chatbot and gr.ChatInterface to display tool use or thinking UIs.