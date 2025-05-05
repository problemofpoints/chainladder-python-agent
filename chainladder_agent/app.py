import gradio as gr
import chainladder as cl
import os
from chainladder_agent.agents.supervisor import create_chainladder_supervisor

# Define commonly used triangle datasets
datasets = [
    'clrd',
    'genins',
    'raa',
    'abc',
    'ukmotor',
    'qtr',
    'quarterly',
    'auto',
    'liab',
    'wkcomp',
    'prism'
]

# Debug flag
DEBUG = True

def process_query(message, triangle_name, history, api_key, thread_id=None):
    """
    Process user queries using the chainladder agent system.
    
    Parameters:
        message: The user's query
        triangle_name: Selected triangle dataset
        history: Conversation history
        api_key: OpenAI API key
        thread_id: Optional thread ID for maintaining conversation state
    
    Returns:
        Updated conversation history
    """
    if DEBUG:
        print(f"Processing query: '{message}'")
        print(f"Selected triangle: '{triangle_name}'")
        print(f"History items: {len(history) if history else 0}")
        print(f"API key available: {bool(api_key)}")
    
    # Sanitize triangle name - use default if empty or invalid
    if not triangle_name or triangle_name.strip() == "":
        triangle_name = datasets[0]  # Use the first triangle as default
        if DEBUG:
            print(f"Using default triangle: {triangle_name}")
    
    # Ensure the triangle name is valid
    if triangle_name not in datasets:
        if DEBUG:
            print(f"Triangle name '{triangle_name}' not in available datasets, using default")
        triangle_name = datasets[0]
    
    try:
        # Validate API key
        if not api_key or not api_key.strip():
            return history + [[message, "Error: Please provide an OpenAI API key in the field above."]]
            
        # Initialize the agent
        supervisor = create_chainladder_supervisor(api_key=api_key)
        
        # Prepare the input for the supervisor with explicit triangle name
        input_data = {
            "messages": [{"role": "user", "content": message}],
            "selected_triangle": triangle_name
        }
        
        # Use the thread_id if provided, or create a default one
        # This enables memory persistence across turns
        config = {}
        if thread_id:
            config["configurable"] = {"thread_id": thread_id}
        else:
            # When no thread_id is provided, use a simple default
            config["configurable"] = {"thread_id": "default_thread"}
        
        if DEBUG:
            print(f"Sending to supervisor with triangle: '{triangle_name}'")
        
        # Run the supervisor with config for thread_id
        if DEBUG: print("Sending to supervisor with triangle: '{}'".format(triangle_name))
        result = supervisor.invoke(input_data, config=config)
        if DEBUG: print("Supervisor invoked successfully")
        
        # Extract the response
        response = "I couldn't generate a proper response. Please try again."
        
        # Process the response with more detailed debugging
        if "messages" in result:
            if DEBUG: 
                print(f"Result contains {len(result['messages'])} messages")
                # Print all messages for debugging
                for i, m in enumerate(result["messages"]):
                    print(f"Message {i} details:")
                    print(f"  Type: {type(m)}")
                    if hasattr(m, 'type'):
                        print(f"  Message type attribute: {m.type}")
                    if hasattr(m, 'content'):
                        print(f"  Content preview: {str(m.content)[:50]}...")
                    if isinstance(m, dict):
                        print(f"  Dict keys: {m.keys()}")
                        if 'role' in m:
                            print(f"  Role: {m['role']}")
                        if 'content' in m:
                            print(f"  Content preview: {str(m['content'])[:50]}...")
            
            # Find all AI messages and get the longest/most substantive one
            ai_messages = []
            
            # First, collect all potential AI messages
            for i, m in enumerate(result["messages"]):
                # Check all types of AI/assistant messages
                if hasattr(m, 'type') and m.type == 'ai':
                    # Exclude messages that are clearly not the final answer
                    content = m.content
                    if content and content.strip() != "..." and len(content) > 20 and "transferring" not in content.lower():
                        ai_messages.append((i, content, len(content)))
                        if DEBUG: print(f"Added AI message from index {i}, length: {len(content)}")
                # Also check dictionary-style messages
                elif isinstance(m, dict) and m.get("role") == "assistant":
                    content = m.get("content")
                    if content and len(content) > 20:
                        ai_messages.append((i, content, len(content)))
                        if DEBUG: print(f"Added assistant dict message from index {i}, length: {len(content)}")
            
            # Sort messages by length (longest first) as a heuristic for most complete answer
            ai_messages.sort(key=lambda x: x[2], reverse=True)
            
            if ai_messages:
                # Use the longest message
                best_idx, best_content, _ = ai_messages[0]
                response = best_content
                if DEBUG: print(f"Selected best response from index {best_idx}, length: {len(response)}")
                if DEBUG: print(f"Response preview: {response[:100]}...")
        
        # Use simple tuple format for the chatbot
        new_history = list(history) if history else []
        new_history.append([message, response])
        
        if DEBUG: print(f"Returning history with {len(new_history)} items")
        return new_history
        
    except Exception as e:
        if DEBUG: print(f"Error in process_query: {str(e)}")
        new_history = list(history) if history else []
        new_history.append([message, f"Error: {str(e)}"])
        return new_history


def launch_app():
    """Launch the Gradio interface for the chainladder agent."""
    with gr.Blocks(title="Chainladder AI Assistant") as app:
        # Header and title
        gr.HTML("<h1 style='text-align: center; margin-bottom: 10px;'>Chainladder AI Assistant</h1>")
        gr.HTML("<p style='text-align: center; margin-bottom: 20px;'>An AI assistant for actuarial analysis using the chainladder package</p>")
        
        # API key input in a small row at the top
        with gr.Row():
            api_key = gr.Textbox(
                label="OpenAI API Key", 
                placeholder="Enter your OpenAI API key here", 
                value=os.environ.get("OPENAI_API_KEY", ""),
                type="password"
            )
        
        # Main chat interface - full width
        with gr.Row():
            # Simple chatbot with full-screen format
            chatbot = gr.Chatbot(
                height=600, 
                label="Conversation",
                bubble_full_width=False,
                show_copy_button=True,
                value=[[None, "Welcome to Chainladder AI Assistant! I can help you with actuarial analyses using the chainladder package. You can reference any triangle by name in your questions (e.g., 'Analyze the raa triangle')."]]
            )
        
        # Input and submit
        with gr.Row():
            message = gr.Textbox(
                label="", 
                placeholder="Ask Chainladder AI",
                scale=9,
                show_label=False,
                container=False
            )
            submit = gr.Button("Send", scale=1)
        
        with gr.Row():
            clear = gr.Button("Clear Chat")
        
        # Triangle selection and info moved below the chat
        with gr.Row():
            # Sample triangles info
            gr.Markdown("""
            ## Available Sample Triangles (Optional Reference)
            You can reference any of these triangles directly in your questions without selecting them below.
            For example: "Show me development factors for the ukmotor triangle" or "Analyze genins using Mack Chain Ladder".
            
            - `raa`: Classic RAA reinsurance triangle - cumulative paid losses
            - `abc`: ABC Company dataset - cumulative losses
            - `ukmotor`: UK Motor triangle - cumulative claim amounts
            - `genins`: General Insurance triangle - incremental paid claims
            - `quarterly`: Quarterly development data with incurred and paid values
            - `auto`: Auto insurance data with features for both incurred and paid losses
            
            See the [chainladder documentation](https://chainladder-python.readthedocs.io/) for more details.
            """)
        
        # Examples section
        gr.Markdown("## Example Tasks")
        examples = gr.Examples(
            examples=[
                ["What sample triangles are available in the chainladder package?"],
                ["Analyze the raa triangle using the chain ladder method"],
                ["Compare chainladder and Bornhuetter-Ferguson methods on the abc triangle"],
                ["Create development factor charts for the ukmotor triangle"],
                ["Explain what IBNR means in actuarial science"],
                ["Create diagnostic plots for the clrd triangle"],
            ],
            inputs=[message]
        )
        
        # Define simple callback function (no generator)
        def on_submit(msg, history, key):
            if not msg.strip():
                return history, gr.update(value="")
            
            # Process the query
            # Extract triangle name from message if possible
            triangle_name = None  # Default to None
            
            # Try to detect triangle name from message
            for dataset in datasets:
                if dataset.lower() in msg.lower():
                    triangle_name = dataset
                    break
                    
            # Get or create a thread ID based on the history
            # This ensures conversation continuity
            thread_id = "user_thread_" + str(hash(str(history)) if history else "new")
            
            # Process the query with thread_id for memory persistence
            new_history = process_query(msg, triangle_name, history, key, thread_id)
            return new_history, gr.update(value="")
        
        # Attach event handlers
        submit.click(
            fn=on_submit,
            inputs=[message, chatbot, api_key],
            outputs=[chatbot, message],
        )

        # Also trigger on Enter key
        message.submit(
            fn=on_submit,
            inputs=[message, chatbot, api_key],
            outputs=[chatbot, message],
        )
        
        # Simple clear chat button
        clear.click(
            fn=lambda: [[None, "Welcome to Chainladder AI Assistant! I can help you with loss reserving using the chainladder package. Ask me a question!"]],
            inputs=None,
            outputs=chatbot,
            queue=False
        )
        
    return app


def main():
    """Main function to run the Gradio app."""
    # Check if OPENAI_API_KEY is in environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("You will need to input your API key in the web interface.")
    
    # Launch the app
    app = launch_app()
    app.launch()


if __name__ == "__main__":
    main()
