"""
Trend Analysis Workflow
Analyzes news trends and recommends content strategies
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.base_workflow import BaseWorkflow
from agents.news_gathering_agent import NewsGatheringAgent
from agents.trend_analysis_agent import TrendAnalysisAgent
from agents.content_creation_agent import ContentCreationAgent

from config.config import LOGGING_CONFIG

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['file_path']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrendAnalysisWorkflow(BaseWorkflow):
    """Workflow for analyzing news trends and recommending content"""
    
    def __init__(self, verbose: bool = False):
        """Initialize the workflow with its component agents"""
        super().__init__(
            name="TrendAnalysisWorkflow",
            description="Analyzes news trends and recommends content strategies"
        )
        
        # Initialize agents
        self.news_agent = NewsGatheringAgent(verbose=verbose)
        self.trend_agent = TrendAnalysisAgent(verbose=verbose)
        self.content_agent = ContentCreationAgent(verbose=verbose)
        
        self.verbose = verbose
    
    def run(
        self,
        analysis_days: int = 7,
        categories: Optional[List[str]] = None,
        auto_generate: bool = False
    ) -> Dict[str, Any]:
        """
        Run the trend analysis workflow
        
        Args:
            analysis_days: Number of days to analyze for trends
            categories: Optional list of categories to focus on
            auto_generate: Whether to automatically generate recommended content
            
        Returns:
            Dictionary with workflow results
        """
        logger.info(f"Starting {self.name} workflow")
        start_time = datetime.now()
        
        results = {
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_days": analysis_days,
            "categories": categories or "all",
            "trend_analysis": {},
            "content_recommendations": {},
            "generated_content": {}
        }
        
        try:
            # Step 1: Analyze overall trends
            logger.info(f"Analyzing news trends over the past {analysis_days} days")
            trend_analysis = self.trend_agent.analyze_trends(days=analysis_days)
            results["trend_analysis"] = trend_analysis
            
            # Step 2: Get content recommendations for each category
            content_recommendations = {}
            
            if categories:
                for category in categories:
                    logger.info(f"Getting content recommendations for category: {category}")
                    recommendations = self.trend_agent.recommend_content(category=category)
                    content_recommendations[category] = recommendations
            else:
                logger.info("Getting general content recommendations")
                recommendations = self.trend_agent.recommend_content()
                content_recommendations["general"] = recommendations
            
            results["content_recommendations"] = content_recommendations
            
            # Step 3: Optionally generate recommended content
            if auto_generate and categories:
                generated_content = {}
                
                for category in categories:
                    logger.info(f"Auto-generating content for category: {category}")
                    generation_result = self.content_agent.generate_articles(
                        category=category,
                        num_articles=1  # Generate one article per recommended category
                    )
                    generated_content[category] = generation_result
                
                results["generated_content"] = generated_content
            
            # Complete the results
            results["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results["success"] = True
            
            logger.info(f"Workflow completed successfully in {datetime.now() - start_time}")
            return results
            
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            results["success"] = False
            results["error"] = str(e)
            results["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return results
