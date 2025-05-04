from langchain_core.tools import tool
import chainladder as cl
import datetime
from ..models import ReportRequest, ReportContent, ReportType
from typing import Dict, Any, List


@tool
def generate_analysis_report(params: ReportRequest) -> ReportContent:
    """
    Generate a comprehensive actuarial report based on analysis results.
    
    Creates a structured report with sections for data description, methodology,
    results, and recommendations.
    """
    try:
        # Load the triangle for reference
        triangle = cl.load_sample(params.triangle_name)
        
        # Get current date/time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate report title
        title = f"Actuarial Analysis Report: {params.triangle_name.title()}"
        
        # Generate executive summary
        summary = (
            f"This report presents the results of actuarial analysis performed on the {params.triangle_name} "
            f"triangle dataset using chainladder methods. "
            f"The analysis includes development factor calculations and loss reserve estimates."
        )
        
        # Prepare report sections based on analysis results and report type
        sections = []
        
        # Data section
        sections.append({
            "title": "Dataset Overview",
            "content": (
                f"The analysis was performed on the {params.triangle_name} dataset, which contains "
                f"{triangle.shape[0]} origin periods and {triangle.shape[1]} development periods. "
                f"The data represents {'cumulative' if triangle.is_cumulative else 'incremental'} values "
                f"with a {triangle.grain} grain."
            )
        })
        
        # Development factors section
        if "development_results" in params.analysis_results:
            dev_results = params.analysis_results["development_results"]
            methods = dev_results.get("methods_used", ["Unknown"])
            
            content = (
                f"Development factors were calculated using the {', '.join(methods)} method(s). "
            )
            
            if params.report_type in [ReportType.DETAILED, ReportType.EXECUTIVE]:
                # Add more detailed information for non-summary reports
                content += (
                    "The selected age-to-age factors indicate how losses develop from one period to the next. "
                    "These factors are crucial for projecting ultimate loss values."
                )
            
            sections.append({
                "title": "Development Factors Analysis",
                "content": content
            })
        
        # IBNR section
        if "ibnr_results" in params.analysis_results:
            ibnr_results = params.analysis_results["ibnr_results"]
            
            total_ibnr = sum(ibnr_results.get("ibnr_estimates", {}).values())
            total_ultimate = sum(ibnr_results.get("ultimate_losses", {}).values())
            
            content = (
                f"The estimated total IBNR reserve is {total_ibnr:,.2f}, with projected ultimate losses "
                f"of {total_ultimate:,.2f}. "
            )
            
            if params.report_type == ReportType.DETAILED:
                # Add more technical details for detailed report
                content += (
                    "The IBNR estimates represent the expected future loss emergence based on historical "
                    "development patterns. These estimates are critical for establishing adequate reserves."
                )
            elif params.report_type == ReportType.EXECUTIVE:
                # Add business impact for executive report
                content += (
                    "These reserve estimates should be considered when making financial planning decisions "
                    "and assessing overall risk exposure."
                )
            
            sections.append({
                "title": "IBNR Reserve Estimates",
                "content": content
            })
            
        # Conclusion based on report type
        if params.report_type == ReportType.SUMMARY:
            conclusion = (
                "The analysis provides a basic overview of the development patterns and reserve requirements "
                "based on the historical loss data. Further analysis may be needed for specific business decisions."
            )
        elif params.report_type == ReportType.DETAILED:
            conclusion = (
                "This detailed analysis demonstrates the application of actuarial methods to estimate "
                "ultimate losses and IBNR reserves. The results should be interpreted in consideration of "
                "the underlying assumptions of each method and the quality of the historical data."
            )
        else:  # EXECUTIVE
            conclusion = (
                "The analysis results indicate the expected future loss emergence and reserve requirements "
                "based on historical development patterns. These estimates should inform strategic decisions "
                "regarding capital allocation, pricing, and risk management."
            )
        
        # Visualization references if requested
        viz_refs = None
        if params.include_visualizations and "visualization_paths" in params.analysis_results:
            viz_refs = params.analysis_results["visualization_paths"]
        
        # Create report content
        report = ReportContent(
            title=title,
            summary=summary,
            sections=sections,
            conclusion=conclusion,
            date_generated=current_time,
            visualization_references=viz_refs if params.include_visualizations else None
        )
        
        return report
    
    except Exception as e:
        # Return a minimal report with error information
        return ReportContent(
            title=f"Error Report: {params.triangle_name}",
            summary=f"An error occurred during report generation: {str(e)}",
            sections=[],
            conclusion="Please review the input data and analysis results for errors.",
            date_generated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )


@tool
def explain_actuarial_concept(concept: str) -> Dict[str, str]:
    """
    Explain an actuarial concept in plain language.
    
    Provides clear, non-technical explanations of common actuarial terms and concepts.
    """
    concepts = {
        "ibnr": (
            "Incurred But Not Reported (IBNR) refers to losses that have occurred but haven't yet been "
            "reported to the insurance company. These are estimated based on historical development "
            "patterns and are a crucial component of an insurer's loss reserves."
        ),
        "development factor": (
            "Development factors, also called loss development factors (LDFs) or age-to-age factors, "
            "represent how losses for a given origin period are expected to grow from one valuation "
            "date to the next. They are calculated from historical loss triangles and used to project "
            "ultimate losses."
        ),
        "chain ladder": (
            "The Chain Ladder method is a fundamental actuarial technique for estimating ultimate losses. "
            "It applies development factors to the latest available loss data to project future development. "
            "This method assumes that historical development patterns will repeat in the future."
        ),
        "bornhuetter-ferguson": (
            "The Bornhuetter-Ferguson method is an actuarial technique that combines the Chain Ladder method "
            "with a priori loss estimates. It gives more weight to actual experience for older development "
            "periods and more weight to expected losses for newer periods. This method is particularly useful "
            "when dealing with immature data or volatile loss patterns."
        ),
        "benktander": (
            "The Benktander method is a credibility-weighted approach that combines elements of the Chain "
            "Ladder method and the Expected Loss Ratio method. It iteratively applies a formula that gives "
            "more weight to actual data as development matures."
        ),
        "cape cod": (
            "The Cape Cod method (also known as the Stanard-Bühlmann method) is similar to the Bornhuetter-Ferguson "
            "method but uses the existing data to estimate the expected loss ratio. It provides a way to incorporate "
            "both prior expectations and actual experience when estimating ultimate losses."
        ),
        "triangle": (
            "A loss triangle is a tabular arrangement of loss data, organized by origin period (rows) and "
            "development period or age (columns). It shows how losses develop over time and forms the basis "
            "for actuarial reserving methods."
        ),
        "ultimate loss": (
            "Ultimate loss represents the final value of losses for a given origin period after all claims "
            "have been settled. Actuaries project ultimate losses to determine how much money an insurer "
            "needs to reserve for future claim payments."
        ),
        "tail factor": (
            "A tail factor represents the additional development expected beyond the final development period "
            "in a loss triangle. It accounts for the 'tail' of the development pattern that extends beyond "
            "the observed data and is crucial for estimating ultimate losses for long-tailed lines of business."
        ),
        "loss development": (
            "Loss development refers to the process by which losses change (typically increase) over time as "
            "claims are reported and settled. Understanding this process is fundamental to actuarial reserving."
        ),
        "mack chainladder": (
            "Mack Chainladder is a stochastic extension of the traditional Chain Ladder method that provides "
            "estimates of the variability (standard error) of reserve estimates. It allows actuaries to quantify "
            "the uncertainty in their projections without making distributional assumptions."
        ),
        "bootstrap": (
            "In actuarial science, bootstrap methods use resampling techniques to estimate the distribution of "
            "reserve estimates. This stochastic approach involves generating multiple simulated triangles based "
            "on the original data to create a range of possible outcomes and quantify uncertainty."
        )
    }
    
    # Find the most relevant concept (case-insensitive partial matching)
    concept_lower = concept.lower()
    for key, explanation in concepts.items():
        if key in concept_lower:
            return {
                "concept": key,
                "explanation": explanation,
                "related_concepts": [k for k in concepts.keys() if k != key and k in explanation.lower()][:3]
            }
    
    # If no specific match, provide a general explanation
    return {
        "concept": concept,
        "explanation": (
            f"'{concept}' is an actuarial term that may relate to insurance reserving or pricing. "
            "Actuaries use statistical methods to analyze historical data and make projections about "
            "future losses and reserves. For more specific information, please provide additional context "
            "or ask about a specific actuarial method."
        ),
        "related_concepts": ["triangle", "development factor", "ibnr"]
    }


@tool
def interpret_analysis_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interpret the results of actuarial analyses and provide insights.
    
    Takes raw analysis output and translates it into actionable business insights.
    """
    insights = {
        "key_findings": [],
        "recommendations": [],
        "limitations": [],
        "interpretation": ""
    }
    
    try:
        # Check for IBNR results
        if "ibnr_estimates" in results:
            ibnr = results["ibnr_estimates"]
            total_ibnr = sum(ibnr.values()) if isinstance(ibnr, dict) else 0
            
            # Add key findings about IBNR
            insights["key_findings"].append(f"Total IBNR reserve estimate: {total_ibnr:,.2f}")
            
            # Add recommendations based on IBNR
            if total_ibnr > 0:
                insights["recommendations"].append(
                    "Consider setting aside appropriate reserves to cover the estimated IBNR amount."
                )
            
        # Check for ultimate losses
        if "ultimate_losses" in results:
            ultimate = results["ultimate_losses"]
            total_ultimate = sum(ultimate.values()) if isinstance(ultimate, dict) else 0
            
            # Add key findings about ultimates
            insights["key_findings"].append(f"Total ultimate loss estimate: {total_ultimate:,.2f}")
        
        # Check for method used
        if "method" in results:
            method = results["method"]
            
            # Add limitations based on method
            if method == "chainladder":
                insights["limitations"].append(
                    "The Chain Ladder method assumes that historical development patterns will continue into the future, "
                    "which may not hold if there have been changes in claim handling, case reserving, or other factors."
                )
            elif method == "bornhuetterferguson":
                insights["limitations"].append(
                    "The Bornhuetter-Ferguson method relies on a priori expected losses, which introduces subjectivity "
                    "into the reserve estimate. The quality of the estimate depends on the accuracy of these expectations."
                )
            elif method == "mack_chainladder":
                insights["limitations"].append(
                    "The Mack Chainladder method provides uncertainty estimates but assumes that development factors "
                    "in different years are uncorrelated, which may not be realistic."
                )
        
        # Generate overall interpretation
        if insights["key_findings"]:
            insights["interpretation"] = (
                "Based on the analysis results, the estimated future loss emergence indicates "
                f"{insights['key_findings'][0].lower()[0:-1]}. "
            )
            
            if insights["limitations"]:
                insights["interpretation"] += (
                    f"However, it's important to note that {insights['limitations'][0].lower()} "
                    "This should be considered when using these results for decision-making."
                )
                
            if insights["recommendations"]:
                insights["interpretation"] += (
                    f" {insights['recommendations'][0]}"
                )
        
        return insights
        
    except Exception as e:
        return {
            "error": str(e),
            "key_findings": ["Unable to interpret results due to an error."],
            "recommendations": ["Review the raw results manually."],
            "limitations": ["Automated interpretation encountered an error."],
            "interpretation": f"Error during interpretation: {str(e)}"
        }
