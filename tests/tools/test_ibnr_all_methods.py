            ultimate = pd.DataFrame(result.ultimate_losses).iloc[-1]
            ibnr = pd.DataFrame(result.ibnr_estimates).iloc[-1]
            
            print(f"  Ultimate Loss (latest year): {ultimate.values[0]:.2f}")
            print(f"  IBNR Estimate (latest year): {ibnr.values[0]:.2f}")
            
            results[method] = {
                "ultimate": ultimate.values[0],
                "ibnr": ibnr.values[0]
            }
        except Exception as e:
            print(f"  ✗ {method} failed: {str(e)}")
    
    print("\n=== Summary of Results ===")
    if len(results) == len(methods):
        print("All methods completed successfully!")
        
        # Create a comparison table
        comparison = pd.DataFrame(results).T
        print("\nComparison of IBNR estimates:")
        print(comparison)
    else:
        print(f"Only {len(results)} out of {len(methods)} methods completed successfully.")
    
    return len(results) == len(methods)

def test_with_apriori():
    """Test methods that accept apriori values with custom apriori."""
    
    # Test data
    triangle_name = "raa"
    
    # Create a simple apriori dictionary - these are just example values
    # Use string keys to satisfy Pydantic validation
    apriori = {
        "1981": 1000.0,
        "1982": 1100.0,
        "1983": 1200.0,
        "1984": 1300.0,
        "1985": 1400.0,
        "1986": 1500.0,
        "1987": 1600.0,
        "1988": 1700.0,
        "1989": 1800.0,
        "1990": 1900.0
    }
    
    # Test methods that use apriori
    methods = ["bornhuetterferguson", "benktander", "capecod"]
    results = {}
    
    print("\n=== Testing Methods with Custom Apriori ===")
    
    for method in methods:
        print(f"\nTesting {method} with apriori...")
        try:
            # For Benktander, we'll test with different iterations
            if method == "benktander":
                # Use invoke method instead of direct call
                result = calculate_ibnr.invoke({
                    "triangle_name": triangle_name, 
                    "method": method, 
                    "apriori": apriori, 
                    "n_iters": 5
                })
            else:
                # Use invoke method instead of direct call
                result = calculate_ibnr.invoke({
                    "triangle_name": triangle_name, 
                    "method": method, 
                    "apriori": apriori
                })
                
            print(f"  ✓ {method} with apriori completed successfully")
            
            # Print some key results
            ultimate = pd.DataFrame(result.ultimate_losses).iloc[-1]
            ibnr = pd.DataFrame(result.ibnr_estimates).iloc[-1]
            
            print(f"  Ultimate Loss (latest year): {ultimate.values[0]:.2f}")
            print(f"  IBNR Estimate (latest year): {ibnr.values[0]:.2f}")
            
            results[method] = {
                "ultimate": ultimate.values[0],
                "ibnr": ibnr.values[0]
            }
