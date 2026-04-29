#!/usr/bin/env python3
"""Jira Deep Analysis CLI Tool"""

import argparse
import sys
from pathlib import Path
from backend.services.cli.analyzer import JiraAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Jira Deep Analysis CLI")
    parser.add_argument("jira_key", help="Jira issue key (e.g., PROJ-123)")
    parser.add_argument("-c", "--config", default="config.yaml", help="Config file path")
    parser.add_argument("-r", "--refresh", action="store_true", help="Force refresh all data sources")
    parser.add_argument("-o", "--output", help="Output directory (overrides config)")
    parser.add_argument("--mock", action="store_true", help="Use mock Jira data for testing")

    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        print("Create config.yaml from config.yaml.example")
        sys.exit(1)

    analyzer = JiraAnalyzer(config_path, use_mock_jira=args.mock)

    if args.refresh:
        print("\n" + "="*60)
        print("FORCE REFRESH MODE")
        print("="*60)
        analyzer.refresh_all()

    result = analyzer.analyze(args.jira_key, output_dir=args.output)

if __name__ == "__main__":
    main()
