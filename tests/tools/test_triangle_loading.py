import chainladder as cl
import sys
from chainladder_agent.tools.data_tools import load_sample_triangle, list_available_triangles, get_triangle_summary, validate_triangle
from chainladder_agent.models import TriangleInfo

def test_triangle_loading():
    """Test the triangle loading functionality and print detailed information."""
    print("1. Testing list_available_triangles:")
    try:
        # Use invoke() method instead of direct calling
        triangles = list_available_triangles.invoke({})
        print(f"Available triangles: {triangles}")
        print(f"Count: {len(triangles)}")
    except Exception as e:
        print(f"Error listing triangles: {e}")
        import traceback
        traceback.print_exc()
    
    # Test all known triangle names to verify they load correctly
    print("\n2. Testing load_sample_triangle with each available triangle:")
    for triangle_name in triangles:
        print(f"\nLoading {triangle_name}:")
        try:
            # Try our tool function with invoke()
            triangle_info = load_sample_triangle.invoke({"sample_name": triangle_name})
            print(f"  Shape: {triangle_info.shape}")
            print(f"  Columns: {triangle_info.columns[:3]}{'...' if len(triangle_info.columns) > 3 else ''}")
            print(f"  Is cumulative: {triangle_info.is_cumulative}")
            print(f"  Grain: {triangle_info.grain}")
        except Exception as e:
            print(f"  ERROR loading {triangle_name}: {e}")
    
    print("\n3. Testing get_triangle_summary with genins:")
    try:
        summary = get_triangle_summary.invoke({"sample_name": "genins"})
        print(f"  Triangle name: {summary.name}")
        print(f"  Shape: {summary.shape}")
        print(f"  Is cumulative: {summary.is_cumulative}")
        print(f"  Grain: {summary.grain}")
        print(f"  Latest diagonal keys: {list(summary.latest_diagonal.keys())[:3]}{'...' if len(summary.latest_diagonal) > 3 else ''}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\n4. Testing validate_triangle with quarterly:")
    try:
        validation = validate_triangle.invoke({"sample_name": "quarterly"})
        print(f"  Is valid: {validation.is_valid}")
        print(f"  Check results: {validation.checks}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\n5. Testing with a non-existent triangle (should show error):")
    try:
        result = load_sample_triangle.invoke({"sample_name": "nonexistent"})
        print(f"  Triangle name: {result.name}")
        print(f"  Shape: {result.shape}")
        # The error should be in the columns field
        print(f"  Error message in columns: {result.columns[0] if result.columns else 'No error message'}") 
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_triangle_loading()
