#!/usr/bin/env python3
"""
Docker utility script for the Agentic News Workflow System
"""

import argparse
import os
import subprocess
import sys

def run_command(command, capture_output=False):
    """Run a shell command and handle errors"""
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                check=True, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout
        else:
            subprocess.run(command, check=True, shell=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error details: {e}")
        if capture_output and e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def build_images(service=None):
    """Build Docker images
    
    Args:
        service: Optional service name to build ('workflow' or 'review')
               If None, builds all services
    """
    # Show summary of what will be built
    if service:
        print(f"Building Docker image for service: {service}")
    else:
        print("Building Docker images for all services:")
        print("- workflow: Main workflow service for scraping and generating content")
        print("- review: Review interface service with web UI")
    
    command = f"docker-compose build {service if service else ''}"
    return run_command(command)

def start_services():
    """Start Docker services"""
    print("Starting services...")
    return run_command("docker-compose up -d")

def stop_services():
    """Stop Docker services"""
    print("Stopping services...")
    return run_command("docker-compose down")

def view_logs(service=None, follow=False):
    """View logs for services"""
    if service:
        command = f"docker-compose logs {'-f' if follow else ''} {service}"
    else:
        command = f"docker-compose logs {'-f' if follow else ''}"
    
    print(f"Viewing logs for {'all services' if not service else service}...")
    return run_command(command)

def check_status():
    """Check the status of services"""
    print("Checking service status...")
    return run_command("docker-compose ps", capture_output=True)

def execute_command(service, command):
    """Execute a command in a service container"""
    print(f"Executing command in {service}: {command}")
    return run_command(f"docker-compose exec {service} {command}")

def main():
    """Parse arguments and execute commands"""
    parser = argparse.ArgumentParser(description="Docker utility for Agentic News Workflow")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build Docker images")
    build_parser.add_argument("--service", "-s", choices=["workflow", "review"], 
                             help="Service to build (workflow or review). If not specified, builds all services.")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start services")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop services")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View service logs")
    logs_parser.add_argument("--service", "-s", help="Service name (workflow or review)")
    logs_parser.add_argument("--follow", "-f", action="store_true", help="Follow logs")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check service status")
    
    # Execute command
    exec_parser = subparsers.add_parser("exec", help="Execute a command in a service")
    exec_parser.add_argument("service", help="Service name (workflow or review)")
    exec_parser.add_argument("cmd", help="Command to execute")
    
    # Run workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Run the workflow in the container")
    workflow_parser.add_argument("--category", "-c", help="Category filter (technology, leadership)")
    
    args = parser.parse_args()
    
    # Execute the appropriate function based on the command
    if args.command == "build":
        result = build_images(args.service if hasattr(args, 'service') else None)
    elif args.command == "start":
        result = start_services()
    elif args.command == "stop":
        result = stop_services()
    elif args.command == "logs":
        result = view_logs(args.service, args.follow)
    elif args.command == "status":
        status_output = check_status()
        if status_output:
            print("\nService Status:")
            print("---------------")
            print(status_output)
        result = bool(status_output)
    elif args.command == "exec":
        result = execute_command(args.service, args.cmd)
    elif args.command == "workflow":
        cmd = "python run_workflow.py"
        if args.category:
            cmd += f" --category {args.category}"
        result = execute_command("workflow", cmd)
    else:
        parser.print_help()
        return 1
    
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
