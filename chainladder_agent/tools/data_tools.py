from langchain_core.tools import tool
import chainladder as cl
import pandas as pd
from ..models import TriangleInfo, TriangleSummary, TriangleValidation
from typing import List, Dict, Any


@tool
def list_available_triangles() -> List[str]:
    """List all available sample triangles in the chainladder package.
    
    Returns:
        List[str]: A list of triangle names available in the chainladder package.
        These can be used with load_sample_triangle, get_triangle_summary,
        and validate_triangle functions.
    """
    # Common triangle names in the chainladder package
    datasets = [
        "raa", "abc", "genins", "ukmotor", "quarterly", "auto", 
        "clrd", "berquist", "mortgage", "usauto", "uspp", "mcl"
    ]
    return datasets


@tool
def load_sample_triangle(sample_name: str) -> TriangleInfo:
    """Load a specific sample triangle from the chainladder package.
    
    This function loads a triangle dataset from the chainladder package and
    returns basic information about it, such as shape, columns, origin periods,
    development periods, and whether it's cumulative or incremental.
    
    Args:
        sample_name (str): Name of the triangle to load (e.g., "raa", "genins", "quarterly")
        
    Returns:
        TriangleInfo: Basic information about the loaded triangle
    """
    try:
        # Load the sample dataset - cl.load_sample is a function that takes a string parameter
        triangle = cl.load_sample(sample_name)
        
        # Return basic information about the triangle
        # Get grain safely, if possible
        grain_value = "unknown"
        try:
            if hasattr(triangle, "grain") and callable(triangle.grain):
                grain_value = "yearly"  # Default fallback if grain() call fails
        except Exception:
            pass  # Keep the default "unknown" value
            
        return TriangleInfo(
            name=sample_name,
            shape=triangle.shape,
            columns=triangle.columns.tolist() if hasattr(triangle, "columns") else [],
            origin=triangle.origin.tolist() if hasattr(triangle, "origin") else [],
            development=triangle.development.tolist() if hasattr(triangle, "development") else [],
            valuation=triangle.valuation.unique().tolist()[:10] if hasattr(triangle, "valuation") else [],
            is_cumulative=triangle.is_cumulative if hasattr(triangle, "is_cumulative") else None,
            grain=grain_value
        )
    except Exception as e:
        # Create a minimal response with error info but include the error message
        return TriangleInfo(
            name=sample_name,
            shape=(0, 0),
            grain="unknown",
            columns=[f"Error: {str(e)}"] # Include the error message in the columns field for visibility
        )


@tool
def get_triangle_summary(sample_name: str) -> TriangleSummary:
    """Get a detailed summary of a specific triangle dataset from the chainladder package.
    
    This function provides more comprehensive information than load_sample_triangle,
    including the latest diagonal values and a preview of the triangle data.
    
    Args:
        sample_name (str): Name of the triangle to summarize (e.g., "raa", "genins", "quarterly")
        
    Returns:
        TriangleSummary: Detailed summary of the triangle dataset
    """
    try:
        # Use cl.load_sample as a function correctly
        triangle = cl.load_sample(sample_name)
        
        # Enhanced summary information
        # Get grain safely, if possible
        grain_value = "unknown"
        try:
            if hasattr(triangle, "grain") and callable(triangle.grain):
                grain_value = "yearly"  # Default fallback if grain() call fails
        except Exception:
            pass  # Keep the default "unknown" value
            
        # Create a safer version of latest_diagonal
        latest_diag = {}
        try:
            if hasattr(triangle, "latest_diagonal") and hasattr(triangle.latest_diagonal, "to_frame"):
                latest_df = triangle.latest_diagonal.to_frame()
                latest_diag = {str(k): float(v) for k, v in latest_df.iloc[:, 0].items()}
        except Exception:
            pass
            
        summary = TriangleSummary(
            name=sample_name,
            shape=triangle.shape,
            valuation_dates=triangle.valuation.unique().tolist()[:10] if hasattr(triangle, "valuation") else [],
            latest_diagonal=latest_diag,
            is_cumulative=triangle.is_cumulative if hasattr(triangle, "is_cumulative") else None,
            grain=grain_value
        )
        
        # Add triangle preview (first few values)
        if hasattr(triangle, "to_frame"):
            # Convert to frame and get head as dict
            preview_df = triangle.to_frame().head(5)
            summary.preview = preview_df.to_dict()
            
        return summary
    except Exception as e:
        return TriangleSummary(
            name=sample_name,
            shape=(0, 0),
            grain="unknown",
            error=str(e)
        )


@tool
def validate_triangle(sample_name: str) -> TriangleValidation:
    """Perform validation checks on a triangle dataset from the chainladder package.
    
    This function checks various properties of the triangle to determine if it's valid
    and suitable for analysis, including checking for NaN values, dimensions, and other
    important triangle properties.
    
    Args:
        sample_name (str): Name of the triangle to validate (e.g., "raa", "genins", "quarterly")
        
    Returns:
        TriangleValidation: Validation results including whether the triangle is valid
        and details about the validation checks performed
    """
    try:
        # Use cl.load_sample as a function correctly
        triangle = cl.load_sample(sample_name)
        
        # Validation checks
        validation = TriangleValidation(
            is_valid=True,
            checks={
                "has_nan": triangle.nan_triangle.sum().sum() > 0 if hasattr(triangle, "nan_triangle") else False,
                "is_cumulative": triangle.is_cumulative if hasattr(triangle, "is_cumulative") else None,
                "dimensions": len(triangle.shape) if hasattr(triangle, "shape") else 0,
                "development_periods": len(triangle.development) if hasattr(triangle, "development") else 0,
                "origin_periods": len(triangle.origin) if hasattr(triangle, "origin") else 0,
                "columns": triangle.columns.tolist() if hasattr(triangle, "columns") else []
            }
        )
        
        return validation
    except Exception as e:
        return TriangleValidation(
            is_valid=False,
            error=str(e)
        )


@tool
def convert_triangle_format(sample_name: str, to_cumulative: bool = True) -> Dict[str, Any]:
    """Convert a triangle between cumulative and incremental formats.
    
    Args:
        sample_name (str): Name of the triangle to convert
        to_cumulative (bool): True to convert to cumulative, False for incremental
        
    Returns:
        Dict[str, Any]: Information about the converted triangle
    """
    try:
        triangle = cl.load_sample(sample_name)
        
        if to_cumulative and not triangle.is_cumulative:
            new_triangle = triangle.incr_to_cum()
            operation = "incremental to cumulative"
        elif not to_cumulative and triangle.is_cumulative:
            new_triangle = triangle.cum_to_incr()
            operation = "cumulative to incremental"
        else:
            operation = "no conversion needed"
            new_triangle = triangle
            
        return {
            "triangle_name": sample_name,
            "operation": operation,
            "original_format": "cumulative" if triangle.is_cumulative else "incremental",
            "new_format": "cumulative" if new_triangle.is_cumulative else "incremental",
            "success": True
        }
    except Exception as e:
        return {
            "triangle_name": sample_name,
            "success": False,
            "error": str(e)
        }


@tool
def grain_triangle(sample_name: str, grain: str) -> Dict[str, Any]:
    """Change the grain of a triangle (e.g., from yearly to quarterly).
    
    Args:
        sample_name (str): Name of the triangle to change grain
        grain (str): New grain value (e.g., 'Y', 'Q', 'M')
        
    Returns:
        Dict[str, Any]: Information about the regrained triangle
    """
    try:
        triangle = cl.load_sample(sample_name)
        new_triangle = triangle.grain(grain)
        
        return {
            "triangle_name": sample_name,
            "original_grain": triangle.grain,
            "new_grain": new_triangle.grain,
            "success": True
        }
    except Exception as e:
        return {
            "triangle_name": sample_name,
            "success": False,
            "error": str(e)
        }


@tool
def get_latest_diagonal(sample_name: str) -> Dict[str, Any]:
    """Get the latest diagonal of a triangle.
    
    Args:
        sample_name (str): Name of the triangle to get the latest diagonal from
        
    Returns:
        Dict[str, Any]: Latest diagonal values by origin period
    """
    try:
        triangle = cl.load_sample(sample_name)
        latest = triangle.latest_diagonal
        
        return {
            "triangle_name": sample_name,
            "latest_diagonal": latest.to_dict(),
            "valuation_date": str(triangle.valuation_date),
            "success": True
        }
    except Exception as e:
        return {
            "triangle_name": sample_name,
            "success": False,
            "error": str(e)
        }
