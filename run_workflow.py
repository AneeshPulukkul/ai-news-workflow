#!/usr/bin/env python3
"""
Main workflow runner for the Agentic News Workflow System
This script orchestrates the complete workflow: scraping -> generation -> review
"""

import sys
import os
import logging
import argparse
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Rich for better console output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from scrapers.news_scraper import NewsAggregator
from content_generator.content_generator import ContentGenerator, ContentDatabase
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


class WorkflowRunner:
    """Main workflow orchestrator for the Agentic News Workflow System"""
    
    def __init__(self):
        """Initialize the workflow runner with all required components"""
        self.news_aggregator = NewsAggregator()
        self.content_generator = ContentGenerator()
        self.content_database = ContentDatabase()
        self.console = Console()

    def _display_scraping_summary(self, summary: Dict[str, Any]):
        """Display scraping summary in a rich table"""
        table = Table(title="Scraping Workflow Summary")
        table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        table.add_row("Start Time", summary['start_time'])
        table.add_row("End Time", summary['end_time'])
        table.add_row("Total Articles Scraped", str(summary['total_articles_scraped']))
        table.add_row("Total Articles Saved", str(summary['total_articles_saved']))

        self.console.print(table)

        category_table = Table(title="Scraped Articles by Category")
        category_table.add_column("Category", style="green")
        category_table.add_column("Count", style="blue")

        for category, count in summary['articles_by_category'].items():
            category_table.add_row(category.title(), str(count))
        
        self.console.print(category_table)

    def _display_content_summary(self, summary: Dict[str, Any]):
        """Display content generation summary in a rich table"""
        gen_summary = summary.get('generation_summary', {})
        
        table = Table(title="Content Generation Summary")
        table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        table.add_row("Source Articles Used", str(gen_summary.get('total_source_articles', 0)))
        table.add_row("Generated Articles", str(len(summary.get('articles', []))))
        table.add_row("Generated Social Posts", str(len(summary.get('posts', []))))
        
        if 'categories' in gen_summary:
            table.add_row("Categories Processed", ", ".join(c.title() for c in gen_summary['categories']))

        self.console.print(table)

    def run_daily_workflow(self, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the complete daily workflow
        
        Args:
            categories: Optional list of categories to filter by
            
        Returns:
            Dictionary with workflow results
        """
        self.console.print(Panel.fit("🚀 Starting Agentic News Workflow 🚀", style="bold green"))
        start_time = datetime.now()
        
        try:
            # Step 1: Scrape news
            with self.console.status("[bold yellow]Step 1: Scraping news articles...", spinner="dots") as status:
                scraping_result = self.news_aggregator.run_daily_scraping()
                self.console.log("Scraping complete.")
            self._display_scraping_summary(scraping_result)
            
            # Add a small delay
            time.sleep(1)
            
            # Step 2: Generate content
            with self.console.status("[bold yellow]Step 2: Generating content...", spinner="dots") as status:
                if categories:
                    content_results = []
                    for category in categories:
                        status.update(f"Generating content for category: {category.title()}")
                        content_result = self.content_generator.generate_daily_content(category)
                        content_results.append(content_result)
                        
                        if content_result.get('articles') or content_result.get('posts'):
                            self.content_database.save_generated_content(content_result)
                            self.console.log(f"Saved content for {category.title()}.")
                    
                    # Combine results
                    combined_result = {
                        'articles': [], 'posts': [],
                        'generation_summary': {
                            'total_source_articles': sum(r['generation_summary']['total_source_articles'] for r in content_results),
                            'articles_generated': sum(len(r.get('articles', [])) for r in content_results),
                            'posts_generated': sum(len(r.get('posts', [])) for r in content_results),
                            'categories': categories
                        }
                    }
                    for result in content_results:
                        combined_result['articles'].extend(result.get('articles', []))
                        combined_result['posts'].extend(result.get('posts', []))
                    
                    content_generation_result = combined_result
                else:
                    status.update("Generating content for all categories...")
                    content_generation_result = self.content_generator.generate_daily_content()
                    if content_generation_result.get('articles') or content_generation_result.get('posts'):
                        self.content_database.save_generated_content(content_generation_result)
                        self.console.log("Saved all generated content.")

                self.console.log("Content generation complete.")
            
            self._display_content_summary(content_generation_result)

            # Final summary
            end_time = datetime.now()
            total_duration = str(end_time - start_time)
            
            final_panel = Panel(
                f"Workflow finished in [bold]{total_duration}[/bold].\n"
                f"Generated [bold green]{len(content_generation_result.get('articles', []))}[/bold green] articles and "
                f"[bold blue]{len(content_generation_result.get('posts', []))}[/bold blue] social posts.",
                title="✅ Workflow Complete ✅",
                border_style="green"
            )
            self.console.print(final_panel)

            return {
                "scraping_summary": scraping_result,
                "content_summary": content_generation_result
            }
            
        except Exception as e:
            self.console.print_exception()
            self.console.print(Panel(f"Workflow failed: {e}", title="❌ Error ❌", border_style="red"))
            return {"error": str(e)}

    def run_scraping_only(self):
        """Run only the news scraping component"""
        logger.info("Running news scraping only")
        try:
            result = self.news_aggregator.run_daily_scraping()
            logger.info(f"Scraping completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_generation_only(self, category=None):
        """Run only the content generation component"""
        logger.info(f"Running content generation only for category: {category or 'all'}")
        try:
            content_result = self.content_generator.generate_daily_content(category)
            
            if content_result['articles'] or content_result['posts']:
                self.content_database.save_generated_content(content_result)
                logger.info(f"Generated and saved: {len(content_result['articles'])} articles, {len(content_result['posts'])} posts")
            
            return content_result['generation_summary']
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_status(self):
        """Get current system status"""
        try:
            # Get recent articles count
            recent_articles = self.news_aggregator.get_daily_articles()
            
            # Get pending content
            pending_content = self.content_database.get_pending_content()
            
            return {
                'recent_articles': len(recent_articles),
                'pending_articles': len(pending_content['articles']),
                'pending_posts': len(pending_content['posts']),
                'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {'error': str(e)}


def main():
    """Main entry point with command line interface"""
    parser = argparse.ArgumentParser(description='Agentic News Workflow System')
    parser.add_argument('--mode', choices=['full', 'scrape', 'generate', 'status'], 
                       default='full', help='Workflow mode to run')
    parser.add_argument('--category', choices=['technology', 'leadership'], 
                       help='Category filter for content generation')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize workflow runner
    runner = WorkflowRunner()
    
    # Execute based on mode
    if args.mode == 'full':
        categories = [args.category] if args.category else None
        result = runner.run_daily_workflow(categories)
        print(f"Daily workflow result: {result}")
    
    elif args.mode == 'scrape':
        result = runner.run_scraping_only()
        print(f"Scraping result: {result}")
    
    elif args.mode == 'generate':
        result = runner.run_generation_only(args.category)
        print(f"Generation result: {result}")
    
    elif args.mode == 'status':
        status = runner.get_status()
        print(f"System status: {status}")
        result = {'success': True}
    
    return 0 if result.get('success', True) else 1


if __name__ == "__main__":
    sys.exit(main())

