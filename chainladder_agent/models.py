from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any, Tuple
from enum import Enum
import datetime


# Core models for Triangle data
class TriangleInfo(BaseModel):
    """Information about a chainladder Triangle."""
    name: str
    shape: tuple
    columns: List[str] = Field(default_factory=list)
    origin: List[Any] = Field(default_factory=list)
    development: List[Any] = Field(default_factory=list)
    valuation: List[Any] = Field(default_factory=list)
    is_cumulative: Optional[bool] = None
    grain: str = "unknown"


class TriangleSummary(BaseModel):
    """Detailed summary of a triangle dataset."""
    name: str
    shape: tuple
    valuation_dates: List[Any] = Field(default_factory=list)
    latest_diagonal: Dict[str, Any] = Field(default_factory=dict)
    is_cumulative: Optional[bool] = None
    grain: str = "unknown"
    preview: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TriangleValidation(BaseModel):
    """Validation results for a triangle."""
    is_valid: bool
    checks: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# Development models
class DevelopmentMethod(str, Enum):
    """Development method options."""
    VOLUME = "volume"
    SIMPLE = "simple"
    REGRESSION = "regression"
    SELECTED = "selected"


class DevelopmentParams(BaseModel):
    """Input for development analysis."""
    triangle_name: str
    methods: List[str] = Field(default_factory=lambda: ["volume"])
    averages: Optional[List[int]] = None
    n_periods: Optional[int] = None


class DevelopmentResult(BaseModel):
    """Result of development analysis."""
    triangle_name: str
    methods_used: List[str]
    averages_used: Optional[List[int]] = None
    link_ratios: Dict[str, Any] = Field(default_factory=dict)
    selected_link_ratios: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# Tail models
class TailMethod(str, Enum):
    """Tail method options."""
    CONSTANT = "constant" 
    CURVE = "curve"
    BONDY = "bondy"
    CLARK = "clark"


class TailParams(BaseModel):
    """Input for tail methods."""
    triangle_name: str
    tail_method: TailMethod = TailMethod.CONSTANT
    tail_factor: Optional[float] = None
    fit_period: Optional[str] = None
    extrap_periods: Optional[int] = None


class TailResult(BaseModel):
    """Result from tail method application."""
    triangle_name: str
    tail_method: str
    tail_factor: float
    development_factors: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# IBNR models
class IBNRMethod(str, Enum):
    """IBNR method options."""
    CHAINLADDER = "chainladder"
    MACK_CHAINLADDER = "mack_chainladder"
    BORNHUETTERFERGUSON = "bornhuetterferguson"
    BENKTANDER = "benktander"
    CAPECOD = "capecod"


class IBNRParams(BaseModel):
    """Input for IBNR calculation."""
    triangle_name: str
    development_triangle_name: Optional[str] = None
    method: IBNRMethod = IBNRMethod.CHAINLADDER
    apriori: Optional[Dict[str, float]] = None
    n_iters: Optional[int] = None
    n_simulations: Optional[int] = None


class IBNRResult(BaseModel):
    """Result of IBNR calculation."""
    triangle_name: str
    method: str
    ultimate_losses: Dict[str, Any] = Field(default_factory=dict)
    ibnr_estimates: Dict[str, Any] = Field(default_factory=dict)
    latest_diagonal: Dict[str, Any] = Field(default_factory=dict)
    std_err: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Visualization models
class PlotType(str, Enum):
    """Types of plots available."""
    HEATMAP = "heatmap"
    DEVELOPMENT = "development"
    ULTIMATES = "ultimates"
    RESIDUALS = "residuals"
    COMPARISON = "comparison"
    ACTUAL_VS_EXPECTED = "actual_vs_expected"


class VisualizationParams(BaseModel):
    """Input for visualization tools."""
    triangle_name: str
    plot_type: PlotType = PlotType.DEVELOPMENT
    title: Optional[str] = None
    cumulative: Optional[bool] = None
    compare_with: Optional[str] = None


class VisualizationResult(BaseModel):
    """Result of visualization creation."""
    triangle_name: str
    plot_type: str
    image_path: str
    error: Optional[str] = None


# Report models
class ReportType(str, Enum):
    """Types of reports that can be generated."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    EXECUTIVE = "executive"


class ReportSection(BaseModel):
    """A section in a report."""
    title: str
    content: str
    visuals: Optional[List[str]] = None


class ReportRequest(BaseModel):
    """Request for generating a report."""
    triangle_name: str
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    report_type: ReportType = ReportType.SUMMARY
    include_visualizations: bool = True


class ReportContent(BaseModel):
    """Content of a generated report."""
    title: str
    summary: str
    sections: List[Dict[str, str]]
    conclusion: str
    date_generated: str
    visualization_references: Optional[List[str]] = None


# State schema for the supervisor
class AgentState(BaseModel):
    """State maintained by the supervisor."""
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    active_agent: Optional[str] = None
    selected_triangle: Optional[str] = None
    development_triangle: Optional[str] = None
    ibnr_triangle: Optional[str] = None
    visualization_paths: List[str] = Field(default_factory=list)
    report: Optional[Dict[str, Any]] = None
