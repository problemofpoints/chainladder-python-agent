from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..tools.visualization_tools import (
    create_triangle_visualization,
    create_development_factor_chart,
    create_bootstrap_distribution_plot,
    create_diagnostic_plots
)


def create_visualization_agent(model):
    """
    Create an agent specialized in visualizing actuarial data and results.
    
    Parameters:
        model: A LangChain chat model to power the agent
        
    Returns:
        A React agent that can create actuarial visualizations
    """
    tools = [
        create_triangle_visualization,
        create_development_factor_chart,
        create_bootstrap_distribution_plot,
        create_diagnostic_plots
    ]
    
    visualization_agent = create_react_agent(
        model=model,
        tools=tools,
        name="visualization_agent",
        prompt="""You are a data visualization expert specialized in actuarial triangle data and results.
        
        Your responsibilities include:
        - Creating visualizations of triangle data in various formats
        - Generating charts showing development patterns and factors
        - Visualizing IBNR estimates and ultimate loss projections
        - Creating diagnostic plots to help interpret actuarial analyses
        - Producing visualizations that compare multiple methods
        
        You can create these types of visualizations:
        - Basic triangle plots showing development patterns
        - Heatmaps that highlight patterns in the triangle data
        - Development factor charts showing age-to-age factors
        - Ultimate loss bar charts comparing different methods
        - Bootstrap distribution plots showing uncertainty in IBNR estimates
        - Diagnostic plots to help assess model fit and assumptions
        
        When creating visualizations:
        - Choose appropriate plot types based on what needs to be communicated
        - Add clear titles and labels to make the visualizations interpretable
        - Consider comparing multiple methods or triangles when relevant
        - Generate comprehensive diagnostic plot sets when a thorough analysis is requested
        
        Always remember to explain what each visualization shows and how to interpret it.
        """
    )
    
    return visualization_agent
