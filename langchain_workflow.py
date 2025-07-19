#!/usr/bin/env python3
"""
Main script for the enhanced Agentic News Workflow System
Provides a CLI interface to run different workflows
"""

import os
import sys
import argparse
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from workflows.standard_workflow import StandardNewsToContentWorkflow
from workflows.trend_analysis_workflow import TrendAnalysisWorkflow
from workflows.fact_checking_workflow import FactCheckingWorkflow
from config.config import LOGGING_CONFIG, NEWS_SOURCES

# Rich for better console output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

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


class WorkflowCLI:
    """Command Line Interface for the Agentic News Workflow System"""
    
    def __init__(self):
        """Initialize the CLI with a rich console"""
        self.console = Console()
    
    def print_header(self):
        """Print the application header"""
        self.console.print(Panel.fit(
            "[bold cyan]Agentic News Workflow System[/bold cyan]\n"
            "[italic]Enhanced with LangChain for multiple agentic flows[/italic]",
            border_style="cyan"
        ))
    
    def print_workflow_result(self, result: Dict[str, Any]):
        """Print workflow result in a readable format"""
        if not result.get("success", False):
            self.console.print(Panel(
                f"[bold red]Workflow failed:[/bold red] {result.get('error', 'Unknown error')}",
                border_style="red"
            ))
            return
        
        # Print summary info
        self.console.print(Panel(
            f"[bold green]Workflow completed successfully[/bold green]\n"
            f"Started: {result.get('start_time')}\n"
            f"Finished: {result.get('end_time')}",
            border_style="green"
        ))
        
        # Print more detailed results based on workflow type
        if "categories" in result:
            self.console.print("[bold]Categories processed:[/bold]", ", ".join(result["categories"]))
        
        if "total_articles_generated" in result:
            self.console.print(f"[bold]Total articles generated:[/bold] {result['total_articles_generated']}")
        
        if "total_posts_generated" in result:
            self.console.print(f"[bold]Total social posts generated:[/bold] {result['total_posts_generated']}")
    
    def run_standard_workflow(self, args):
        """Run the standard news-to-content workflow"""
        self.console.print(Panel("[bold]Running Standard News-to-Content Workflow[/bold]"))
        
        # Parse categories
        categories = args.categories.split(",") if args.categories else list(NEWS_SOURCES.keys())
        
        # Create and run workflow
        workflow = StandardNewsToContentWorkflow(verbose=args.verbose)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Running workflow...", total=100)
            
            # Run the workflow
            result = workflow.run(
                categories=categories,
                articles_per_category=args.articles_per_category,
                generate_social_posts=not args.no_social_posts,
                verify_facts=not args.no_fact_check
            )
            
            progress.update(task, completed=100)
        
        # Print results
        self.print_workflow_result(result)
    
    def run_trend_analysis(self, args):
        """Run the trend analysis workflow"""
        self.console.print(Panel("[bold]Running Trend Analysis Workflow[/bold]"))
        
        # Parse categories
        categories = args.categories.split(",") if args.categories else None
        
        # Create and run workflow
        workflow = TrendAnalysisWorkflow(verbose=args.verbose)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Analyzing trends...", total=100)
            
            # Run the workflow
            result = workflow.run(
                analysis_days=args.days,
                categories=categories,
                auto_generate=args.auto_generate
            )
            
            progress.update(task, completed=100)
        
        # Print results
        self.print_workflow_result(result)
    
    def run_fact_checking(self, args):
        """Run the fact checking workflow"""
        self.console.print(Panel("[bold]Running Fact Checking Workflow[/bold]"))
        
        # Parse article IDs
        article_ids = [int(id_str) for id_str in args.article_ids.split(",")]
        
        # Create and run workflow
        workflow = FactCheckingWorkflow(verbose=args.verbose)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Checking facts...", total=100)
            
            # Run the workflow
            result = workflow.run(
                article_ids=article_ids,
                confidence_threshold=args.threshold,
                auto_correct=args.auto_correct
            )
            
            progress.update(task, completed=100)
        
        # Print results
        self.print_workflow_result(result)

    def parse_args(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="Agentic News Workflow System - Enhanced with LangChain"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Workflow to run")
        
        # Standard workflow parser
        standard_parser = subparsers.add_parser("standard", help="Run the standard news-to-content workflow")
        standard_parser.add_argument(
            "--categories", 
            help="Comma-separated list of categories (default: all in config)"
        )
        standard_parser.add_argument(
            "--articles-per-category", 
            type=int, 
            default=2,
            help="Number of articles to generate per category (default: 2)"
        )
        standard_parser.add_argument(
            "--no-social-posts", 
            action="store_true",
            help="Disable social post generation"
        )
        standard_parser.add_argument(
            "--no-fact-check", 
            action="store_true",
            help="Disable fact checking"
        )
        standard_parser.add_argument(
            "--verbose", 
            action="store_true",
            help="Enable verbose output"
        )
        
        # Trend analysis parser
        trend_parser = subparsers.add_parser("trends", help="Run the trend analysis workflow")
        trend_parser.add_argument(
            "--days", 
            type=int, 
            default=7,
            help="Number of days to analyze (default: 7)"
        )
        trend_parser.add_argument(
            "--categories", 
            help="Comma-separated list of categories to focus on (default: all)"
        )
        trend_parser.add_argument(
            "--auto-generate", 
            action="store_true",
            help="Automatically generate recommended content"
        )
        trend_parser.add_argument(
            "--verbose", 
            action="store_true",
            help="Enable verbose output"
        )
        
        # Fact checking parser
        fact_parser = subparsers.add_parser("factcheck", help="Run the fact checking workflow")
        fact_parser.add_argument(
            "article_ids", 
            help="Comma-separated list of article IDs to check"
        )
        fact_parser.add_argument(
            "--threshold", 
            type=float, 
            default=0.7,
            help="Confidence threshold for facts (0.0 to 1.0, default: 0.7)"
        )
        fact_parser.add_argument(
            "--auto-correct", 
            action="store_true",
            help="Automatically attempt to correct inaccurate content"
        )
        fact_parser.add_argument(
            "--verbose", 
            action="store_true",
            help="Enable verbose output"
        )
        
        return parser.parse_args()
    
    def run(self):
        """Run the CLI application"""
        args = self.parse_args()
        
        self.print_header()
        
        if args.command == "standard":
            self.run_standard_workflow(args)
        elif args.command == "trends":
            self.run_trend_analysis(args)
        elif args.command == "factcheck":
            self.run_fact_checking(args)
        else:
            self.console.print("[bold red]Please specify a workflow to run.[/bold red]")
            self.console.print("Available workflows: standard, trends, factcheck")
            self.console.print("Example: python langchain_workflow.py standard --categories technology,business")


if __name__ == "__main__":
    cli = WorkflowCLI()
    cli.run()
