"""
Monitoring system for guardrails to track performance and identify improvement opportunities.
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
import sqlite3

logger = logging.getLogger(__name__)

class GuardrailMonitor:
    """
    System to monitor, log, and analyze guardrail activations.
    
    This class provides:
    1. Logging of guardrail events to a database
    2. Metrics and reporting on guardrail performance
    3. Analysis to identify improvement opportunities
    4. Audit trail for compliance and accountability
    """
    
    def __init__(self, db_path: str = "data/guardrail_events.db"):
        """
        Initialize the guardrail monitor.
        
        Args:
            db_path: Path to the SQLite database for storing events
        """
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Create the database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS guardrail_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            guardrail_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            content_id TEXT,
            workflow_id TEXT,
            agent_id TEXT,
            details TEXT,
            user_feedback TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS guardrail_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            guardrail_name TEXT NOT NULL,
            invocations INTEGER DEFAULT 0,
            blocks INTEGER DEFAULT 0,
            modifications INTEGER DEFAULT 0,
            passes INTEGER DEFAULT 0,
            false_positives INTEGER DEFAULT 0,
            false_negatives INTEGER DEFAULT 0
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_event(
        self, 
        guardrail_name: str, 
        event_type: str, 
        details: Dict[str, Any],
        content_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> int:
        """
        Log a guardrail event to the database.
        
        Args:
            guardrail_name: Name of the guardrail
            event_type: Type of event (block, modify, pass)
            details: Details about the event
            content_id: ID of the content being processed
            workflow_id: ID of the workflow
            agent_id: ID of the agent
            
        Returns:
            ID of the inserted event
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert details to JSON string
        details_json = json.dumps(details)
        
        # Insert event
        cursor.execute(
            '''
            INSERT INTO guardrail_events 
            (timestamp, guardrail_name, event_type, content_id, workflow_id, agent_id, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                datetime.now().isoformat(),
                guardrail_name,
                event_type,
                content_id,
                workflow_id,
                agent_id,
                details_json
            )
        )
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Also update daily metrics
        self._update_daily_metrics(guardrail_name, event_type)
        
        return event_id
    
    def _update_daily_metrics(self, guardrail_name: str, event_type: str) -> None:
        """Update the daily metrics for a guardrail."""
        today = datetime.now().date().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if we have a record for today
        cursor.execute(
            "SELECT id FROM guardrail_metrics WHERE date = ? AND guardrail_name = ?",
            (today, guardrail_name)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing record
            metric_id = result[0]
            if event_type == "block":
                cursor.execute(
                    "UPDATE guardrail_metrics SET invocations = invocations + 1, blocks = blocks + 1 WHERE id = ?",
                    (metric_id,)
                )
            elif event_type == "modify":
                cursor.execute(
                    "UPDATE guardrail_metrics SET invocations = invocations + 1, modifications = modifications + 1 WHERE id = ?",
                    (metric_id,)
                )
            elif event_type == "pass":
                cursor.execute(
                    "UPDATE guardrail_metrics SET invocations = invocations + 1, passes = passes + 1 WHERE id = ?",
                    (metric_id,)
                )
        else:
            # Create new record
            blocks = 1 if event_type == "block" else 0
            modifications = 1 if event_type == "modify" else 0
            passes = 1 if event_type == "pass" else 0
            
            cursor.execute(
                '''
                INSERT INTO guardrail_metrics 
                (date, guardrail_name, invocations, blocks, modifications, passes)
                VALUES (?, ?, 1, ?, ?, ?)
                ''',
                (today, guardrail_name, blocks, modifications, passes)
            )
        
        conn.commit()
        conn.close()
    
    def record_user_feedback(self, event_id: int, feedback: str) -> None:
        """
        Record user feedback about a guardrail event.
        
        Args:
            event_id: ID of the guardrail event
            feedback: User feedback (e.g., "false_positive", "helpful", etc.)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE guardrail_events SET user_feedback = ? WHERE id = ?",
            (feedback, event_id)
        )
        
        # If feedback indicates false positive or negative, update metrics
        if feedback in ["false_positive", "false_negative"]:
            cursor.execute(
                "SELECT guardrail_name, timestamp FROM guardrail_events WHERE id = ?",
                (event_id,)
            )
            result = cursor.fetchone()
            
            if result:
                guardrail_name, timestamp_str = result
                timestamp = datetime.fromisoformat(timestamp_str)
                date = timestamp.date().isoformat()
                
                if feedback == "false_positive":
                    cursor.execute(
                        "UPDATE guardrail_metrics SET false_positives = false_positives + 1 WHERE date = ? AND guardrail_name = ?",
                        (date, guardrail_name)
                    )
                else:  # false_negative
                    cursor.execute(
                        "UPDATE guardrail_metrics SET false_negatives = false_negatives + 1 WHERE date = ? AND guardrail_name = ?",
                        (date, guardrail_name)
                    )
        
        conn.commit()
        conn.close()
    
    def get_metrics(
        self, 
        guardrail_name: Optional[str] = None, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get metrics for guardrails.
        
        Args:
            guardrail_name: Filter by guardrail name (None for all)
            start_date: Start date in ISO format (None for all time)
            end_date: End date in ISO format (None for today)
            
        Returns:
            Dictionary of metrics
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        query = "SELECT * FROM guardrail_metrics WHERE 1=1"
        params = []
        
        if guardrail_name:
            query += " AND guardrail_name = ?"
            params.append(guardrail_name)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Calculate aggregate metrics
        metrics = {
            "total_invocations": 0,
            "total_blocks": 0,
            "total_modifications": 0,
            "total_passes": 0,
            "total_false_positives": 0,
            "total_false_negatives": 0,
            "block_rate": 0.0,
            "modification_rate": 0.0,
            "pass_rate": 0.0,
            "false_positive_rate": 0.0,
            "by_guardrail": {},
            "by_date": {}
        }
        
        for row in rows:
            row_dict = dict(row)
            guardrail = row_dict["guardrail_name"]
            date = row_dict["date"]
            
            # Update totals
            metrics["total_invocations"] += row_dict["invocations"]
            metrics["total_blocks"] += row_dict["blocks"]
            metrics["total_modifications"] += row_dict["modifications"]
            metrics["total_passes"] += row_dict["passes"]
            metrics["total_false_positives"] += row_dict["false_positives"]
            metrics["total_false_negatives"] += row_dict["false_negatives"]
            
            # Update by guardrail
            if guardrail not in metrics["by_guardrail"]:
                metrics["by_guardrail"][guardrail] = {
                    "invocations": 0,
                    "blocks": 0,
                    "modifications": 0,
                    "passes": 0,
                    "false_positives": 0,
                    "false_negatives": 0
                }
            
            metrics["by_guardrail"][guardrail]["invocations"] += row_dict["invocations"]
            metrics["by_guardrail"][guardrail]["blocks"] += row_dict["blocks"]
            metrics["by_guardrail"][guardrail]["modifications"] += row_dict["modifications"]
            metrics["by_guardrail"][guardrail]["passes"] += row_dict["passes"]
            metrics["by_guardrail"][guardrail]["false_positives"] += row_dict["false_positives"]
            metrics["by_guardrail"][guardrail]["false_negatives"] += row_dict["false_negatives"]
            
            # Update by date
            if date not in metrics["by_date"]:
                metrics["by_date"][date] = {
                    "invocations": 0,
                    "blocks": 0,
                    "modifications": 0,
                    "passes": 0,
                    "false_positives": 0,
                    "false_negatives": 0
                }
            
            metrics["by_date"][date]["invocations"] += row_dict["invocations"]
            metrics["by_date"][date]["blocks"] += row_dict["blocks"]
            metrics["by_date"][date]["modifications"] += row_dict["modifications"]
            metrics["by_date"][date]["passes"] += row_dict["passes"]
            metrics["by_date"][date]["false_positives"] += row_dict["false_positives"]
            metrics["by_date"][date]["false_negatives"] += row_dict["false_negatives"]
        
        # Calculate rates
        if metrics["total_invocations"] > 0:
            metrics["block_rate"] = metrics["total_blocks"] / metrics["total_invocations"]
            metrics["modification_rate"] = metrics["total_modifications"] / metrics["total_invocations"]
            metrics["pass_rate"] = metrics["total_passes"] / metrics["total_invocations"]
            
            total_interventions = metrics["total_blocks"] + metrics["total_modifications"]
            if total_interventions > 0:
                metrics["false_positive_rate"] = metrics["total_false_positives"] / total_interventions
        
        # Calculate rates for each guardrail
        for guardrail, guardrail_metrics in metrics["by_guardrail"].items():
            if guardrail_metrics["invocations"] > 0:
                guardrail_metrics["block_rate"] = guardrail_metrics["blocks"] / guardrail_metrics["invocations"]
                guardrail_metrics["modification_rate"] = guardrail_metrics["modifications"] / guardrail_metrics["invocations"]
                guardrail_metrics["pass_rate"] = guardrail_metrics["passes"] / guardrail_metrics["invocations"]
                
                total_interventions = guardrail_metrics["blocks"] + guardrail_metrics["modifications"]
                if total_interventions > 0:
                    guardrail_metrics["false_positive_rate"] = guardrail_metrics["false_positives"] / total_interventions
        
        conn.close()
        return metrics
    
    def get_recent_events(
        self, 
        limit: int = 100, 
        guardrail_name: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent guardrail events.
        
        Args:
            limit: Maximum number of events to return
            guardrail_name: Filter by guardrail name
            event_type: Filter by event type
            
        Returns:
            List of event dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM guardrail_events WHERE 1=1"
        params = []
        
        if guardrail_name:
            query += " AND guardrail_name = ?"
            params.append(guardrail_name)
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            row_dict = dict(row)
            # Parse the JSON details
            if row_dict["details"]:
                row_dict["details"] = json.loads(row_dict["details"])
            events.append(row_dict)
        
        conn.close()
        return events
    
    def identify_improvement_opportunities(self) -> Dict[str, Any]:
        """
        Analyze guardrail data to identify improvement opportunities.
        
        Returns:
            Dictionary with improvement suggestions
        """
        # Get metrics for the last 30 days
        end_date = datetime.now().date().isoformat()
        start_date = (datetime.now() - timedelta(days=30)).date().isoformat()
        metrics = self.get_metrics(start_date=start_date, end_date=end_date)
        
        opportunities = {
            "high_false_positive_guardrails": [],
            "low_efficacy_guardrails": [],
            "frequently_triggered_guardrails": [],
            "rarely_triggered_guardrails": [],
            "recommendations": []
        }
        
        # Analyze each guardrail
        for guardrail, guardrail_metrics in metrics["by_guardrail"].items():
            # High false positive rate (>20%)
            if guardrail_metrics.get("false_positive_rate", 0) > 0.2:
                opportunities["high_false_positive_guardrails"].append({
                    "guardrail": guardrail,
                    "false_positive_rate": guardrail_metrics["false_positive_rate"],
                    "invocations": guardrail_metrics["invocations"]
                })
                
                opportunities["recommendations"].append({
                    "guardrail": guardrail,
                    "issue": "High false positive rate",
                    "recommendation": "Adjust threshold or refine detection patterns to reduce false positives."
                })
            
            # Low efficacy (rarely blocks/modifies when invoked, <5%)
            intervention_rate = (guardrail_metrics.get("block_rate", 0) + 
                               guardrail_metrics.get("modification_rate", 0))
            if intervention_rate < 0.05 and guardrail_metrics["invocations"] > 50:
                opportunities["low_efficacy_guardrails"].append({
                    "guardrail": guardrail,
                    "intervention_rate": intervention_rate,
                    "invocations": guardrail_metrics["invocations"]
                })
                
                opportunities["recommendations"].append({
                    "guardrail": guardrail,
                    "issue": "Low intervention rate",
                    "recommendation": "Consider adjusting threshold or expanding detection patterns."
                })
            
            # Frequently triggered (>20% of total invocations)
            if guardrail_metrics["invocations"] > 0.2 * metrics["total_invocations"]:
                opportunities["frequently_triggered_guardrails"].append({
                    "guardrail": guardrail,
                    "invocation_percentage": guardrail_metrics["invocations"] / metrics["total_invocations"],
                    "invocations": guardrail_metrics["invocations"]
                })
                
                if guardrail_metrics.get("false_positive_rate", 0) < 0.1:
                    opportunities["recommendations"].append({
                        "guardrail": guardrail,
                        "issue": "Frequently triggered with good accuracy",
                        "recommendation": "This guardrail is effective and should be maintained."
                    })
            
            # Rarely triggered (<1% of total invocations)
            if guardrail_metrics["invocations"] < 0.01 * metrics["total_invocations"]:
                opportunities["rarely_triggered_guardrails"].append({
                    "guardrail": guardrail,
                    "invocation_percentage": guardrail_metrics["invocations"] / metrics["total_invocations"],
                    "invocations": guardrail_metrics["invocations"]
                })
                
                opportunities["recommendations"].append({
                    "guardrail": guardrail,
                    "issue": "Rarely triggered",
                    "recommendation": "Evaluate if this guardrail is necessary or if it should be adjusted."
                })
        
        # Check for patterns in false positives
        false_positive_events = self.get_recent_events(
            limit=1000, 
            event_type="block"
        )
        
        false_positives = [e for e in false_positive_events if e.get("user_feedback") == "false_positive"]
        if false_positives:
            # In a real implementation, we would analyze patterns in the content
            # For now, just count by guardrail
            guardrail_counts = {}
            for event in false_positives:
                guardrail = event["guardrail_name"]
                guardrail_counts[guardrail] = guardrail_counts.get(guardrail, 0) + 1
            
            for guardrail, count in guardrail_counts.items():
                if count >= 10:  # Arbitrary threshold
                    opportunities["recommendations"].append({
                        "guardrail": guardrail,
                        "issue": f"Pattern of false positives ({count} instances)",
                        "recommendation": "Review and adjust detection patterns based on false positive examples."
                    })
        
        return opportunities
    
    def generate_audit_report(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an audit report for compliance purposes.
        
        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format
            
        Returns:
            Audit report data
        """
        # Get metrics
        metrics = self.get_metrics(start_date=start_date, end_date=end_date)
        
        # Get sample events for each guardrail and event type
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sample_events = {}
        for guardrail in metrics["by_guardrail"].keys():
            sample_events[guardrail] = {}
            
            for event_type in ["block", "modify", "pass"]:
                cursor.execute(
                    "SELECT * FROM guardrail_events WHERE guardrail_name = ? AND event_type = ? ORDER BY timestamp DESC LIMIT 5",
                    (guardrail, event_type)
                )
                rows = cursor.fetchall()
                
                sample_events[guardrail][event_type] = []
                for row in rows:
                    row_dict = dict(row)
                    if row_dict["details"]:
                        row_dict["details"] = json.loads(row_dict["details"])
                    sample_events[guardrail][event_type].append(row_dict)
        
        conn.close()
        
        # Generate the report
        report = {
            "report_generated": datetime.now().isoformat(),
            "period_start": start_date,
            "period_end": end_date,
            "metrics": metrics,
            "sample_events": sample_events,
            "compliance_summary": {
                "total_content_processed": metrics["total_invocations"],
                "content_blocked": metrics["total_blocks"],
                "content_modified": metrics["total_modifications"],
                "content_passed": metrics["total_passes"],
                "false_positives": metrics["total_false_positives"],
                "false_negatives": metrics["total_false_negatives"],
                "compliance_rate": metrics["pass_rate"] + metrics["modification_rate"]
            }
        }
        
        return report
