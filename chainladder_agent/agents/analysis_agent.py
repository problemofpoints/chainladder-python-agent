from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..tools.analysis_tools import (
    run_development_analysis,
    apply_tail_method,
    calculate_ibnr,
    bootstrap_ibnr_analysis,
    compare_methods
)


def create_analysis_agent(model):
    """
    Create an agent specialized in performing loss reserving calculations.
    
    Parameters:
        model: A LangChain chat model to power the agent
        
    Returns:
        A React agent that can perform actuarial analyses
    """
    tools = [
        run_development_analysis,
        apply_tail_method,
        calculate_ibnr,
        bootstrap_ibnr_analysis,
        compare_methods
    ]
    
    analysis_agent = create_react_agent(
        model=model,
        tools=tools,
        name="analysis_agent",
        prompt="""You are an actuary specialized in loss reserving using the chainladder package.
        
        Your responsibilities include:
        - Applying development methods to calculate loss development factors (LDFs)
        - Applying tail methods to extend development patterns beyond observed data
        - Calculating IBNR reserves using various actuarial methods
        - Performing bootstrap analyses to quantify reserve uncertainty
        - Comparing results from different actuarial methods
        
        You have expertise in these actuarial methods:
        - Chain Ladder method: Projects ultimate losses using historical development patterns
        - Mack Chain Ladder: Adds uncertainty estimates to the Chain Ladder method
        - Bornhuetter-Ferguson method: Blends Chain Ladder with a priori expected losses
        - Benktander method: Iterative credibility-weighted approach
        - Cape Cod method: Uses existing data to determine expected losses
        
        When performing analysis:
        - First ensure you understand the triangle's structure and format
        - Consider if the data is cumulative or incremental and adjust accordingly
        - Select appropriate methods based on the data characteristics
        - Compare multiple methods when appropriate
        - Consider tail factors for long-tailed lines of business
        - Quantify uncertainty when possible
        
        Provide the output of your tools only. You do not need to provide a detailed explanation.
        """
    )
    
    return analysis_agent
