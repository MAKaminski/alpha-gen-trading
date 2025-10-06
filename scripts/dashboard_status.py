#!/usr/bin/env python3
"""Generate live dashboard status for README.md"""

import subprocess
import json
import os
from datetime import datetime
from pathlib import Path


def run_command(cmd):
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"Error: {e}", 1


def get_test_status():
    """Get current test status."""
    print("Running tests to get current status...")
    
    # Run tests and capture output
    cmd = "python -m pytest tests/unit/ --tb=no -q --json-report --json-report-file=/tmp/test_results.json"
    stdout, returncode = run_command(cmd)
    
    # Try to read JSON results
    try:
        with open('/tmp/test_results.json', 'r') as f:
            results = json.load(f)
        
        total = results.get('summary', {}).get('total', 0)
        passed = results.get('summary', {}).get('passed', 0)
        failed = results.get('summary', {}).get('failed', 0)
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': round((passed / total * 100) if total > 0 else 0, 1)
        }
    except Exception:
        # Fallback to parsing stdout
        lines = stdout.split('\n')
        for line in lines:
            if 'failed' in line and 'passed' in line:
                # Parse line like "36 failed, 199 passed, 10 warnings in 1.69s"
                parts = line.split()
                try:
                    failed = int(parts[0])
                    passed = int(parts[2])
                    total = passed + failed
                    return {
                        'total': total,
                        'passed': passed,
                        'failed': failed,
                        'success_rate': round((passed / total * 100) if total > 0 else 0, 1)
                    }
                except (ValueError, IndexError):
                    pass
    
    return {'total': 0, 'passed': 0, 'failed': 0, 'success_rate': 0}


def get_coverage_status():
    """Get current coverage status."""
    print("Getting coverage status...")
    
    cmd = "python -m pytest tests/unit/ --cov=src/alphagen --cov-report=term --cov-report=json:/tmp/coverage.json"
    stdout, returncode = run_command(cmd)
    
    try:
        with open('/tmp/coverage.json', 'r') as f:
            coverage_data = json.load(f)
        
        total_lines = coverage_data.get('totals', {}).get('num_statements', 0)
        covered_lines = coverage_data.get('totals', {}).get('covered_lines', 0)
        coverage_percent = coverage_data.get('totals', {}).get('percent_covered', 0)
        
        return {
            'total_lines': total_lines,
            'covered_lines': covered_lines,
            'coverage_percent': round(coverage_percent, 1)
        }
    except Exception:
        # Parse from stdout
        lines = stdout.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                try:
                    parts = line.split()
                    coverage_str = parts[-1].replace('%', '')
                    coverage_percent = float(coverage_str)
                    return {
                        'total_lines': 0,
                        'covered_lines': 0,
                        'coverage_percent': coverage_percent
                    }
                except (ValueError, IndexError):
                    pass
    
    return {'total_lines': 0, 'covered_lines': 0, 'coverage_percent': 0}


def check_vercel_status():
    """Check if Vercel deployment is accessible."""
    print("Checking Vercel deployment status...")
    
    # Check if we can reach the Vercel deployment
    cmd = "curl -s -o /dev/null -w '%{http_code}' https://alpha-gen.vercel.app"
    stdout, returncode = run_command(cmd)
    
    if returncode == 0 and stdout == '200':
        return {'status': 'online', 'url': 'https://alpha-gen.vercel.app'}
    else:
        return {'status': 'offline', 'url': 'https://alpha-gen.vercel.app'}


def generate_dashboard_summary():
    """Generate a dashboard summary."""
    print("Generating dashboard summary...")
    
    test_status = get_test_status()
    coverage_status = get_coverage_status()
    vercel_status = check_vercel_status()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    summary = {
        'timestamp': timestamp,
        'tests': test_status,
        'coverage': coverage_status,
        'deployment': vercel_status
    }
    
    # Save to file
    output_file = Path('dashboard_status.json')
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Dashboard status saved to {output_file}")
    print(f"Last updated: {timestamp}")
    print(f"Tests: {test_status['passed']}/{test_status['total']} passing ({test_status['success_rate']}%)")
    print(f"Coverage: {coverage_status['coverage_percent']}%")
    print(f"Vercel: {vercel_status['status']}")
    
    return summary


def update_readme_dashboard():
    """Update the README.md with current dashboard status."""
    print("Updating README.md dashboard...")
    
    summary = generate_dashboard_summary()
    
    # Read current README
    readme_path = Path('README.md')
    if not readme_path.exists():
        print("README.md not found!")
        return
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Update test status section
    test_status_text = f"""**Overall Test Status**: **{summary['tests']['passed']} PASSING** | **{summary['tests']['failed']} FAILING** | **{summary['tests']['success_rate']}% Success Rate**"""
    
    # Update coverage section
    coverage_text = f"**Overall Coverage**: **{summary['coverage']['coverage_percent']}%** ({summary['coverage']['covered_lines']}/{summary['coverage']['total_lines']} statements)"
    
    # Update deployment status
    vercel_emoji = "🟢" if summary['deployment']['status'] == 'online' else "🔴"
    deployment_text = f"| **Frontend (Vercel)** | {vercel_emoji} **{summary['deployment']['status'].upper()}** | [{summary['deployment']['url']}]({summary['deployment']['url']}) | {summary['timestamp']} |"
    
    # Update timestamp
    timestamp_text = f"*Last Updated: {summary['timestamp']}* | *Test Status: {summary['tests']['success_rate']}% Passing* | *Coverage: {summary['coverage']['coverage_percent']}% Overall*"
    
    # Replace sections in content
    import re
    
    # Replace test status
    content = re.sub(
        r'\*\*Overall Test Status\*\*: \*\*.*?\*\* \| \*\*.*?\*\* \| \*\*.*?% Success Rate\*\*',
        test_status_text,
        content
    )
    
    # Replace coverage
    content = re.sub(
        r'\*\*Overall Coverage\*\*: \*\*.*?%\*\* \(.*? statements\)',
        coverage_text,
        content
    )
    
    # Replace deployment status
    content = re.sub(
        r'\| \*\*Frontend \(Vercel\)\*\* \| .*? \| .*? \| .*? \|',
        deployment_text,
        content
    )
    
    # Replace timestamp
    content = re.sub(
        r'\*Last Updated: .*?\* \| \*Test Status: .*?% Passing\* \| \*Coverage: .*?% Overall\*',
        timestamp_text,
        content
    )
    
    # Write updated content
    with open(readme_path, 'w') as f:
        f.write(content)
    
    print(f"README.md updated with current dashboard status!")
    print(f"Timestamp: {summary['timestamp']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--update-readme':
        update_readme_dashboard()
    else:
        generate_dashboard_summary()
