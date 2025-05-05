from langgraph_supervisor import create_supervisor
from langchain_openai import ChatOpenAI
from typing import Dict, List, Optional, Any, Sequence
from langgraph.checkpoint.memory import InMemorySaver

# Import the agent creators
from .analysis_agent import create_analysis_agent
from .visualization_agent import create_visualization_agent
from .explanation_agent import create_explanation_agent
from .data_agent import create_data_agent


def create_chainladder_supervisor(api_key=None):
    """
    Create a supervisor agent that coordinates the specialized chainladder agents.
    
    Parameters:
        api_key: OpenAI API key (optional, can be set via env var)
        
    Returns:
        A compiled supervisor workflow that can be invoked
    """
    # Create model with API key if provided
    if api_key:
        model = ChatOpenAI(model="gpt-4.1", api_key=api_key, temperature=0)
    else:
        model = ChatOpenAI(model="gpt-4.1", temperature=0)
    
    # Create specialized agents
    data_agent = create_data_agent(model)
    analysis_agent = create_analysis_agent(model)
    visualization_agent = create_visualization_agent(model)
    explanation_agent = create_explanation_agent(model)
    
    # Create supervisor workflow
    workflow = create_supervisor(
        [analysis_agent, visualization_agent, explanation_agent],
        model=model,
        output_mode="last_message",
        prompt="""You are an actuarial analysis supervisor managing a team of specialized agents.
        
        Your team consists of:
         
        2. ANALYSIS AGENT: Specialized in actuarial analysis methods
           - Use for development factor calculations, tail methods, and IBNR calculations
           - Handles methods like Chain Ladder, Bornhuetter-Ferguson, and stochastic approaches
        
        3. VISUALIZATION AGENT: Specialized in creating visualizations
           - Use for creating triangle plots, development charts, and diagnostic visualizations
           - Can generate comprehensive sets of diagnostic plots
        
        4. EXPLANATION AGENT: Specialized in explaining results and generating reports
           - Use for explaining actuarial concepts in plain language
           - Generates structured reports summarizing the analysis
           - Interprets the business implications of results
        
        Your job is to:
        - Understand the user's request and break it down into steps
        - Delegate tasks to the appropriate specialized agent based on their expertise
        - Maintain context across the conversation and analysis workflow
        - Synthesize results from multiple agents when needed
        - Ensure the user gets a complete and coherent response
        
        When working on a new analysis:
        2. Then use analysis agent to perform the requested actuarial analyses
        3. Use visualization agent to create relevant plots
        4. Finally use explanation agent to generate reports or explain results
        
        Always be goal-oriented and efficient in your delegation.
        """
    )
    
    checkpointer = InMemorySaver()
    # Compile and return the workflow
    return workflow.compile(checkpointer = checkpointer)
