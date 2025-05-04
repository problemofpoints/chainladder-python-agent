from langchain_core.tools import tool
import chainladder as cl
from ..models import (
    DevelopmentParams, 
    DevelopmentResult, 
    TailParams,
    TailResult,
    IBNRParams, 
    IBNRResult
)
from typing import Dict, Any


@tool
def run_development_analysis(params: DevelopmentParams) -> DevelopmentResult:
    """
    Apply development method to estimate loss development factors (LDFs) for a triangle.
    
    This tool implements chainladder's Development class to calculate age-to-age factors
    using methods like volume-weighted average, simple average, or regression.
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(params.triangle_name)
        
        # Set up Development parameters
        dev_params = {}
        if params.methods:
            dev_params["average"] = params.methods
        if params.n_periods:
            dev_params["n_periods"] = params.n_periods
        elif params.averages:
            dev_params["n_periods"] = params.averages
        
        # Run the development
        dev = cl.Development(**dev_params).fit(triangle)
        
        # Get the link ratio details - converting DataFrames to dicts
        link_ratios = {}
        if hasattr(dev, "ldf_"):
            ldf_frame = dev.ldf_.to_frame()
            if not ldf_frame.empty:
                link_ratios = ldf_frame.to_dict()
        
        # Get the selected link ratios
        selected_link_ratios = {}
        if hasattr(dev, "ldf_"):
            selected = dev.ldf_.to_dict()
            if selected:
                selected_link_ratios = selected
        
        # Generate summary of development analysis
        result = DevelopmentResult(
            triangle_name=params.triangle_name,
            methods_used=params.methods,
            averages_used=params.averages or [params.n_periods] if params.n_periods else None,
            link_ratios=link_ratios,
            selected_link_ratios=selected_link_ratios
        )
        
        return result
    except Exception as e:
        return DevelopmentResult(
            triangle_name=params.triangle_name,
            methods_used=params.methods,
            averages_used=params.averages,
            link_ratios={},
            selected_link_ratios={},
            error=f"Development analysis failed: {str(e)}"
        )


@tool
def apply_tail_method(params: TailParams) -> TailResult:
    """
    Apply a tail method to extend development factors beyond the observed data.
    
    Available methods include constant tail factor, curve fitting, Bondy, and Clark methods.
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(params.triangle_name)
        
        # First apply development method to get LDFs
        dev = cl.Development().fit(triangle)
        
        # Apply selected tail method
        tail_params = {}
        
        if params.tail_method == "constant" and params.tail_factor:
            tail_params["tail"] = params.tail_factor
        
        if params.tail_method == "curve" and params.fit_period:
            tail_params["curve"] = params.fit_period
        
        if params.tail_method == "bondy" and params.extrap_periods:
            tail_params["extrap_periods"] = params.extrap_periods
        
        # Create appropriate tail object based on method
        if params.tail_method == "constant":
            tail = cl.TailConstant(**tail_params).fit(dev)
        elif params.tail_method == "curve":
            tail = cl.TailCurve(**tail_params).fit(dev)
        elif params.tail_method == "bondy":
            tail = cl.TailBondy(**tail_params).fit(dev)
        elif params.tail_method == "clark":
            tail = cl.TailClark().fit(dev)
        else:
            raise ValueError(f"Unknown tail method: {params.tail_method}")
        
        # Extract tail factor
        tail_factor = tail.tail_.iloc[0, 0] if hasattr(tail, "tail_") else 1.0
        
        # Get the full development with tail
        full_ldf = tail.ldf_.to_dict() if hasattr(tail, "ldf_") else {}
        
        result = TailResult(
            triangle_name=params.triangle_name,
            tail_method=params.tail_method,
            tail_factor=tail_factor,
            development_factors=full_ldf
        )
        
        return result
    except Exception as e:
        return TailResult(
            triangle_name=params.triangle_name,
            tail_method=params.tail_method,
            tail_factor=1.0,
            error=f"Tail method failed: {str(e)}"
        )


@tool
def calculate_ibnr(params: IBNRParams) -> IBNRResult:
    """
    Calculate IBNR estimates using various actuarial methods.
    
    Available methods include Chain Ladder, Mack Chain Ladder (with uncertainty), 
    Bornhuetter-Ferguson, Benktander, and Cape Cod.
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(params.triangle_name)
        
        # Load or create development triangle
        if params.development_triangle_name:
            dev_triangle = cl.load_sample(params.development_triangle_name)
            dev = dev_triangle  # Assuming it's already a fitted Development object
        else:
            # Apply default development
            dev = cl.Development().fit(triangle)
        
        # Apply selected IBNR method
        if params.method == "chainladder":
            ibnr = cl.Chainladder().fit(dev)
        elif params.method == "mack_chainladder":
            ibnr = cl.MackChainladder().fit(dev)
        elif params.method == "bornhuetterferguson":
            # Using apriori values if provided, otherwise use defaults
            bf_params = {}
            if params.apriori:
                bf_params["apriori"] = params.apriori
            ibnr = cl.BornhuetterFerguson(**bf_params).fit(dev)
        elif params.method == "benktander":
            benk_params = {}
            if params.apriori:
                benk_params["apriori"] = params.apriori
            if params.n_iters:
                benk_params["n_iters"] = params.n_iters
            ibnr = cl.Benktander(**benk_params).fit(dev)
        elif params.method == "capecod":
            cc_params = {}
            if params.apriori:
                cc_params["apriori"] = params.apriori
            ibnr = cl.CapeCod(**cc_params).fit(dev)
        else:
            raise ValueError(f"Unknown IBNR method: {params.method}")
        
        # Get relevant results
        ultimate = ibnr.ultimate_.to_dict() if hasattr(ibnr, "ultimate_") else {}
        ibnr_values = ibnr.ibnr_.to_dict() if hasattr(ibnr, "ibnr_") else {}
        
        # Get standard errors if available (for stochastic methods)
        std_err = None
        if hasattr(ibnr, "full_std_err_"):
            std_err = ibnr.full_std_err_.to_dict()
        
        result = IBNRResult(
            triangle_name=params.triangle_name,
            method=params.method,
            ultimate_losses=ultimate,
            ibnr_estimates=ibnr_values,
            latest_diagonal=triangle.latest_diagonal.to_dict() if hasattr(triangle, "latest_diagonal") else {},
            std_err=std_err
        )
        
        return result
    except Exception as e:
        return IBNRResult(
            triangle_name=params.triangle_name,
            method=params.method,
            ultimate_losses={},
            ibnr_estimates={},
            latest_diagonal={},
            error=f"IBNR calculation failed: {str(e)}"
        )


@tool
def bootstrap_ibnr_analysis(triangle_name: str, n_simulations: int = 1000, random_state: int = 42) -> Dict[str, Any]:
    """
    Perform bootstrap resampling to estimate IBNR and calculate prediction intervals.
    
    This uses the BootstrapODPSample method from chainladder to generate stochastic estimates.
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(triangle_name)
        
        # Apply bootstrap resampling
        sample = cl.BootstrapODPSample(n_sims=n_simulations, random_state=random_state).fit(triangle)
        
        # Apply development and IBNR calculation to the samples
        dev = cl.Development().fit(sample)
        ibnr = cl.Chainladder().fit(dev)
        
        # Extract key statistics
        summary = ibnr.ibnr_.summary()
        
        # Format the results
        result = {
            "triangle_name": triangle_name,
            "n_simulations": n_simulations,
            "ibnr_mean": summary.mean().to_dict(),
            "ibnr_std_dev": summary.std().to_dict(),
            "percentiles": {
                "5%": summary.quantile(0.05).to_dict(),
                "25%": summary.quantile(0.25).to_dict(),
                "50%": summary.quantile(0.50).to_dict(),
                "75%": summary.quantile(0.75).to_dict(),
                "95%": summary.quantile(0.95).to_dict()
            },
            "success": True
        }
        
        return result
    except Exception as e:
        return {
            "triangle_name": triangle_name,
            "success": False,
            "error": str(e)
        }


@tool
def compare_methods(triangle_name: str, methods: list = ["chainladder", "bornhuetterferguson", "benktander"]) -> Dict[str, Any]:
    """
    Compare multiple IBNR methods side by side on the same triangle.
    
    This tool runs multiple IBNR methods and provides a comparison of the results.
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(triangle_name)
        
        # Apply development
        dev = cl.Development().fit(triangle)
        
        results = {}
        
        # Apply each method
        for method in methods:
            if method == "chainladder":
                ibnr = cl.Chainladder().fit(dev)
            elif method == "mack_chainladder":
                ibnr = cl.MackChainladder().fit(dev)
            elif method == "bornhuetterferguson":
                ibnr = cl.BornhuetterFerguson().fit(dev)
            elif method == "benktander":
                ibnr = cl.Benktander().fit(dev)
            elif method == "capecod":
                ibnr = cl.CapeCod().fit(dev)
            else:
                continue
                
            # Store the results
            results[method] = {
                "ultimate": ibnr.ultimate_.to_dict(),
                "ibnr": ibnr.ibnr_.to_dict()
            }
        
        return {
            "triangle_name": triangle_name,
            "methods_compared": methods,
            "results": results,
            "success": True
        }
    except Exception as e:
        return {
            "triangle_name": triangle_name,
            "success": False,
            "error": str(e)
        }
