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
def calculate_ibnr(
    triangle_name: str,
    method: str,
    development_triangle_name: str = None,
    apriori: Dict[str, float] = None,
    n_iters: int = None,
    n_simulations: int = None
) -> IBNRResult:
    """
    Calculate IBNR estimates using various actuarial methods.
    
    Args:
        triangle_name: Name of the triangle to analyze (e.g., 'raa', 'ukmotor', etc.)
        method: Method to use ('chainladder', 'mack_chainladder', 'bornhuetterferguson', 'benktander', or 'capecod')
        development_triangle_name: Optional name of a pre-fitted development triangle
        apriori: Optional dictionary of apriori values for BF, Benktander, or Cape Cod methods
        n_iters: Number of iterations for Benktander method
        n_simulations: Number of simulations for stochastic methods
    
    Returns:
        IBNRResult containing the ultimate losses, IBNR estimates, and other relevant information
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(triangle_name)
        
        # For development, we need to work directly with the triangle
        # We won't use a separate development triangle as that could lead to compatibility issues
        # Instead, we'll apply development methods directly on our main triangle
        
        # Apply selected IBNR method directly to the triangle
        if method == "chainladder":
            # Chain Ladder - simpler method
            # dev_cl = cl.Development(average='simple').fit_transform(triangle)
            ibnr = cl.Chainladder().fit(triangle)
        
        elif method == "mack_chainladder":
            # Mack Chain Ladder needs a development object
            dev_mack = cl.Development().fit_transform(triangle)
            ibnr = cl.MackChainladder().fit(triangle)
        
        elif method == "bornhuetterferguson":
            # Bornhuetter-Ferguson needs both development and apriori values
            dev_bf = cl.Development().fit_transform(triangle)
            
            # If no apriori provided, we'll use the expected CLF value
            if not apriori:
                # Calculate exposure based on latest values
                latest = triangle.latest_diagonal
                # Create a simple exposure as a percentage of total
                total = latest.sum().sum()
                exposure = latest.to_frame()
                exposure = exposure / total * 1000  # Scale to reasonable size
                sample_weight = {k: float(v) for k, v in exposure.iloc[:, 0].items()}
            else:
                sample_weight = apriori
                
            # BF method needs apriori=1 in constructor and sample_weight during fit
            ibnr = cl.BornhuetterFerguson(apriori=1).fit(dev_bf, sample_weight=sample_weight)
        
        elif method == "benktander":
            # Benktander is similar to BF but with iterations
            dev_benk = cl.Development().fit_transform(triangle)
            
            # Default iterations if not specified
            iterations = n_iters if n_iters else 3
            
            # If no apriori provided, we'll use the expected CLF value
            if not apriori:
                # Calculate exposure based on latest values
                latest = triangle.latest_diagonal
                # Create a simple exposure as a percentage of total
                total = latest.sum().sum()
                exposure = latest.to_frame()
                exposure = exposure / total * 1000  # Scale to reasonable size
                sample_weight = {k: float(v) for k, v in exposure.iloc[:, 0].items()}
            else:
                sample_weight = apriori
                
            # Benktander needs apriori=1 in constructor and sample_weight during fit
            ibnr = cl.Benktander(apriori=1, n_iters=iterations).fit(dev_benk, sample_weight=sample_weight)
        
        elif method == "capecod":
            # Cape Cod is similar to BF but uses different exposure allocation
            dev_cc = cl.Development().fit_transform(triangle)
            
            # If no apriori provided, we'll use the latest diagonal values
            if not apriori:
                # Use latest diagonal as sample weight
                latest = triangle.latest_diagonal
                sample_weight = {k: float(v) for k, v in latest.to_frame().iloc[:, 0].items()}
            else:
                sample_weight = apriori
                
            # Cape Cod accepts sample_weight during the fit process
            ibnr = cl.CapeCod().fit(dev_cc, sample_weight=sample_weight)
        
        else:
            raise ValueError(f"Unknown IBNR method: {method}")
        
        # Get relevant results
        ultimate = ibnr.ultimate_.to_dict() if hasattr(ibnr, "ultimate_") else {}
        ibnr_values = ibnr.ibnr_.to_dict() if hasattr(ibnr, "ibnr_") else {}
        
        # Calculate total ultimate losses and total IBNR
        total_ultimate = float(ibnr.ultimate_.sum().sum()) if hasattr(ibnr, "ultimate_") else None
        total_ibnr = float(ibnr.ibnr_.sum().sum()) if hasattr(ibnr, "ibnr_") else None
        
        # Get standard errors if available (for stochastic methods)
        std_err = None
        if hasattr(ibnr, "full_std_err_"):
            # Convert to dictionary and ensure all keys are strings
            std_err_dict = ibnr.full_std_err_.to_dict()
            # Convert any non-string keys to strings to prevent validation errors
            std_err = {}
            for k1, v1 in std_err_dict.items():
                if isinstance(v1, dict):
                    inner_dict = {}
                    for k2, v2 in v1.items():
                        inner_dict[str(k2)] = v2
                    std_err[str(k1)] = inner_dict
                else:
                    std_err[str(k1)] = v1
        
        result = IBNRResult(
            triangle_name=triangle_name,
            method=method,
            ultimate_losses=ultimate,
            ibnr_estimates=ibnr_values,
            latest_diagonal=triangle.latest_diagonal.to_dict() if hasattr(triangle, "latest_diagonal") else {},
            total_ultimate_losses=total_ultimate,
            total_ibnr=total_ibnr,
            std_err=std_err
        )
        
        return result
    except Exception as e:
        return IBNRResult(
            triangle_name=triangle_name,
            method=method,
            ultimate_losses={},
            ibnr_estimates={},
            latest_diagonal={},
            total_ultimate_losses=None,
            total_ibnr=None,
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
