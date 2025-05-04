import chainladder as cl
import inspect

def explore_chainladder_samples():
    """Explore how the chainladder sample data loader works."""
    
    print("Type of cl.load_sample:", type(cl.load_sample))
    
    # If it's a module, let's see what's in it
    if hasattr(cl.load_sample, "__all__"):
        print("\nAvailable sample datasets:", cl.load_sample.__all__)
    
    # Let's see what names are available in the module
    print("\nAttributes available in cl.load_sample:")
    for name in dir(cl.load_sample):
        if not name.startswith("_"):
            attr = getattr(cl.load_sample, name)
            print(f"{name}: {type(attr)}")
    
    # Try loading a sample triangle
    print("\nTrying to load the RAA triangle:")
    try:
        if callable(cl.load_sample):
            # If load_sample is a function, let's see its docstring and signature
            print(f"cl.load_sample docstring: {cl.load_sample.__doc__}")
            print(f"cl.load_sample signature: {inspect.signature(cl.load_sample)}")
            
            # Try calling it with potential arguments
            print("Trying to call cl.load_sample directly:")
            triangle = cl.load_sample("raa")
            print(f"Success! Triangle shape: {triangle.shape}")
        else:
            # Try the normal attribute access
            triangle = cl.load_sample.raa()
            print(f"Success! Triangle shape: {triangle.shape}")
    except Exception as e:
        print(f"Error loading triangle: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explore_chainladder_samples()
