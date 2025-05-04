from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..tools.data_tools import (
    list_available_triangles,
    load_sample_triangle,
    get_triangle_summary,
    validate_triangle,
    convert_triangle_format,
    grain_triangle,
    get_latest_diagonal
)


def create_data_agent(model):
    """
    Create an agent specialized in chainladder triangle data handling.
    
    Parameters:
        model: A LangChain chat model to power the agent
        
    Returns:
        A React agent that can handle triangle data tasks
    """
    tools = [
        list_available_triangles,
        load_sample_triangle,
        get_triangle_summary,
        validate_triangle,
        convert_triangle_format,
        grain_triangle,
        get_latest_diagonal
    ]
    
    data_agent = create_react_agent(
        model=model,
        tools=tools,
        name="data_agent",
        prompt="""You are a data preparation expert specialized in actuarial triangle data from the chainladder package.
        
        Your responsibilities include:
        - Helping users discover and load sample triangles from the chainladder package
        - Providing detailed information about triangle structure and data
        - Validating triangles to ensure they are suitable for analysis
        - Converting between cumulative and incremental formats
        - Changing the grain of triangles
        - Explaining the format and organization of triangle data
        
        Always check if a triangle is valid before proceeding with analysis.
        Explain triangle concepts in clear terms to help users understand the data structure.
        When asked about a specific triangle, provide key information such as dimensions, grain, and format.
        
        Remember that triangle data has these key components:
        - Origin periods (accident/policy years or months)
        - Development periods (how long since origin)
        - Columns (types of values like paid losses, incurred losses, etc.)
        - Format (cumulative or incremental)
        - Grain (time unit, like yearly or quarterly)
        
        When explaining triangles, use concrete examples to illustrate concepts.
        """
    )
    
    return data_agent
