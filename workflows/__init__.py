"""
Workflows package for Agentic News Workflow System
"""

from workflows.base_workflow import BaseWorkflow
from workflows.standard_workflow import StandardNewsToContentWorkflow
from workflows.trend_analysis_workflow import TrendAnalysisWorkflow
from workflows.fact_checking_workflow import FactCheckingWorkflow

__all__ = [
    'BaseWorkflow',
    'StandardNewsToContentWorkflow',
    'TrendAnalysisWorkflow',
    'FactCheckingWorkflow'
]
