from langchain_core.tools import tool
import chainladder as cl
import matplotlib.pyplot as plt
import os
import uuid
from ..models import VisualizationParams, VisualizationResult

# Create directory for storing visualizations if it doesn't exist
os.makedirs("visualizations", exist_ok=True)

@tool
def create_triangle_visualization(params: VisualizationParams) -> VisualizationResult:
    """
    Create a visualization of triangle data.
    
    Generates various plots based on the plot_type parameter, including heatmaps,
    development patterns, ultimate estimates, and residual plots.
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(params.triangle_name)
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Generate different plot types
        if params.plot_type == "heatmap":
            # Create a heatmap of the triangle values
            ax = triangle.to_frame().unstack().plot.heatmap()
            title = params.title or f"Heatmap of {params.triangle_name}"
            
        elif params.plot_type == "development":
            # Plot development patterns
            is_cum = params.cumulative if params.cumulative is not None else triangle.is_cumulative
            ax = triangle.plot(cumulative=is_cum)
            title = params.title or f"Development Patterns for {params.triangle_name}"
            
        elif params.plot_type == "ultimates":
            # First run development and then plot ultimates
            dev = cl.Development().fit(triangle)
            ibnr = cl.IBNR().fit(dev)
            ax = ibnr.ultimate_.plot.bar()
            title = params.title or f"Ultimate Loss Estimates for {params.triangle_name}"
            
        elif params.plot_type == "residuals":
            # Plot residuals from development model
            dev = cl.Development().fit(triangle)
            ax = dev.plot_residuals()
            title = params.title or f"Residual Plot for {params.triangle_name}"
            
        elif params.plot_type == "comparison":
            # Compare methods if compare_with parameter is provided
            if params.compare_with:
                # Get other triangle if it exists
                try:
                    other_triangle = cl.load_sample(params.compare_with)
                    ax = triangle.plot()
                    other_triangle.plot(ax=ax, legend=True)
                    title = params.title or f"Comparison: {params.triangle_name} vs {params.compare_with}"
                except:
                    # Fall back to regular plot if comparison triangle doesn't exist
                    ax = triangle.plot()
                    title = params.title or f"Triangle Plot for {params.triangle_name}"
            else:
                # Run multiple methods and compare them
                dev = cl.Development().fit(triangle)
                cl_ibnr = cl.Chainladder().fit(dev)
                bf_ibnr = cl.BornhuetterFerguson().fit(dev)
                
                ax = cl_ibnr.ultimate_.plot(legend=True, label="Chain Ladder")
                bf_ibnr.ultimate_.plot(ax=ax, legend=True, label="Bornhuetter-Ferguson")
                title = params.title or f"Method Comparison for {params.triangle_name}"
            
        elif params.plot_type == "actual_vs_expected":
            # Plot actual vs expected values
            dev = cl.Development().fit(triangle)
            cl_ibnr = cl.Chainladder().fit(dev)
            
            # Extract latest diagonal (actual) and ultimate (expected)
            latest = triangle.latest_diagonal
            ultimate = cl_ibnr.ultimate_
            
            # Plot them side by side
            combined = cl.concat([latest.rename('Actual'), ultimate.rename('Ultimate')])
            ax = combined.plot.bar(legend=True)
            title = params.title or f"Actual vs Ultimate for {params.triangle_name}"
            
        else:
            # Default to basic plot
            ax = triangle.plot()
            title = params.title or f"Triangle Plot for {params.triangle_name}"
        
        plt.title(title)
        plt.tight_layout()
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"visualizations/{params.triangle_name}_{params.plot_type}_{unique_id}.png"
        
        # Save the figure
        plt.savefig(filename)
        plt.close()
        
        return VisualizationResult(
            triangle_name=params.triangle_name,
            plot_type=str(params.plot_type),
            image_path=os.path.abspath(filename)
        )
        
    except Exception as e:
        return VisualizationResult(
            triangle_name=params.triangle_name,
            plot_type=str(params.plot_type) if params.plot_type else "unknown",
            image_path="",
            error=f"Visualization failed: {str(e)}"
        )


@tool
def create_development_factor_chart(triangle_name: str, methods: list = ["volume", "simple"], n_periods: int = None) -> VisualizationResult:
    """
    Create a chart showing development factors using different methods.
    
    This specializes in visualizing and comparing different LDF calculation methods.
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(triangle_name)
        
        # Set up development params
        dev_params = {"average": methods}
        if n_periods:
            dev_params["n_periods"] = n_periods
        
        # Run development
        dev = cl.Development(**dev_params).fit(triangle)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot LDFs
        ax = dev.ldf_.plot(legend=True)
        
        title = f"Development Factors for {triangle_name} using {', '.join(methods)} methods"
        plt.title(title)
        plt.tight_layout()
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"visualizations/{triangle_name}_dev_factors_{unique_id}.png"
        
        # Save the figure
        plt.savefig(filename)
        plt.close()
        
        return VisualizationResult(
            triangle_name=triangle_name,
            plot_type="development_factors",
            image_path=os.path.abspath(filename)
        )
        
    except Exception as e:
        return VisualizationResult(
            triangle_name=triangle_name,
            plot_type="development_factors",
            image_path="",
            error=f"Development factor chart failed: {str(e)}"
        )


@tool
def create_bootstrap_distribution_plot(triangle_name: str, n_simulations: int = 1000, random_state: int = 42) -> VisualizationResult:
    """
    Create a plot showing the distribution of IBNR estimates from bootstrap resampling.
    
    This visualizes the range and uncertainty in IBNR estimates.
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(triangle_name)
        
        # Apply bootstrap resampling
        sample = cl.BootstrapODPSample(n_sims=n_simulations, random_state=random_state).fit(triangle)
        
        # Apply development and IBNR calculation to the samples
        dev = cl.Development().fit(sample)
        ibnr = cl.Chainladder().fit(dev)
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Plot distribution of total IBNR
        ax = ibnr.ibnr_.sum().plot.hist(bins=30)
        
        title = f"Bootstrap Distribution of IBNR for {triangle_name} (n={n_simulations})"
        plt.title(title)
        plt.xlabel("Total IBNR")
        plt.ylabel("Frequency")
        plt.tight_layout()
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"visualizations/{triangle_name}_bootstrap_{unique_id}.png"
        
        # Save the figure
        plt.savefig(filename)
        plt.close()
        
        return VisualizationResult(
            triangle_name=triangle_name,
            plot_type="bootstrap_distribution",
            image_path=os.path.abspath(filename)
        )
        
    except Exception as e:
        return VisualizationResult(
            triangle_name=triangle_name,
            plot_type="bootstrap_distribution",
            image_path="",
            error=f"Bootstrap distribution plot failed: {str(e)}"
        )


@tool
def create_diagnostic_plots(triangle_name: str) -> dict:
    """
    Create a set of diagnostic plots for a triangle.
    
    Generates multiple visualizations to help analyze the triangle data.
    """
    try:
        # Load the triangle
        triangle = cl.load_sample(triangle_name)
        
        results = []
        
        # 1. Basic development plot
        viz_params = VisualizationParams(
            triangle_name=triangle_name,
            plot_type="development",
            title=f"Development Patterns for {triangle_name}"
        )
        development_plot = create_triangle_visualization(viz_params)
        results.append(development_plot)
        
        # 2. Heatmap
        viz_params.plot_type = "heatmap"
        viz_params.title = f"Heatmap of {triangle_name}"
        heatmap_plot = create_triangle_visualization(viz_params)
        results.append(heatmap_plot)
        
        # 3. Development factors
        dev_factor_plot = create_development_factor_chart(triangle_name)
        results.append(dev_factor_plot)
        
        # 4. Ultimates comparison
        viz_params.plot_type = "comparison"
        viz_params.title = f"Method Comparison for {triangle_name}"
        comparison_plot = create_triangle_visualization(viz_params)
        results.append(comparison_plot)
        
        # Return information about all created visualizations
        return {
            "triangle_name": triangle_name,
            "plot_paths": [result.image_path for result in results if not result.error],
            "success": True
        }
        
    except Exception as e:
        return {
            "triangle_name": triangle_name,
            "success": False,
            "error": str(e)
        }
