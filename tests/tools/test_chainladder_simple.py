import chainladder as cl

def test_chainladder_structure():
    """Test the structure of chainladder triangles"""
    print("Loading RAA triangle...")
    triangle = cl.load_sample("raa")
    
    print(f"\nType: {type(triangle)}")
    print(f"Shape: {triangle.shape}")
    print(f"Is cumulative: {triangle.is_cumulative}")
    
    # Test important attributes carefully
    print("\nBasic properties:")
    for attr_name in ['columns', 'origin', 'development', 'valuation', 'latest_diagonal']:
        try:
            attr = getattr(triangle, attr_name)
            print(f"{attr_name}: {type(attr)}")
            if hasattr(attr, "tolist"):
                print(f"  Value: {attr.tolist()}")
            elif hasattr(attr, "to_frame"):
                print(f"  First few values: {attr.to_frame().head(3)}")
        except Exception as e:
            print(f"{attr_name}: Error - {e}")
    
    # Test grain method specifically
    print("\nTesting grain method:")
    try:
        # First check if it exists and is callable
        if hasattr(triangle, 'grain'):
            grain_attr = getattr(triangle, 'grain')
            print(f"Type of grain: {type(grain_attr)}")
            if callable(grain_attr):
                try:
                    # Try calling it with different parameters
                    # First with no params
                    grain_value = grain_attr()
                    print(f"grain() result: {grain_value}")
                    
                    # Then try a specific format
                    grain_value_str = str(grain_value)
                    print(f"grain() as string: {grain_value_str}")
                except Exception as e:
                    print(f"Error calling grain(): {e}")
            else:
                print(f"grain is not callable: {grain_attr}")
        else:
            print("grain attribute not found")
    except Exception as e:
        print(f"Error testing grain: {e}")
    
    # Try converting to a DataFrame
    print("\nConverting to DataFrame:")
    try:
        df = triangle.to_frame()
        print(df.head())
    except Exception as e:
        print(f"Error converting to DataFrame: {e}")

if __name__ == "__main__":
    test_chainladder_structure()
