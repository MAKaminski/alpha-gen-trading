#!/usr/bin/env python3
"""
Scheduled MCP monitoring for Alpha-Gen project.
Runs regular checks on MCP availability and functionality.
"""

import asyncio
import schedule
import time
import json
from datetime import datetime
from pathlib import Path
from mcp_monitor import MCPMonitor

class ScheduledMCPMonitor:
    """Scheduled monitoring for MCP servers."""
    
    def __init__(self):
        self.monitor = MCPMonitor()
        self.log_file = Path("mcp_monitoring.log")
        self.results_dir = Path("mcp_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def log_message(self, message: str):
        """Log message with timestamp."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        print(f"[{timestamp}] {message}")
    
    async def run_scheduled_check(self):
        """Run a scheduled MCP health check."""
        self.log_message("Starting scheduled MCP health check...")
        
        try:
            # Run health check
            health_results = await self.monitor.run_health_check()
            
            # Save results with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.results_dir / f"mcp_check_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(health_results, f, indent=2)
            
            # Generate summary
            summary = health_results['summary']
            self.log_message(f"MCP Check Complete - Available: {summary['available_servers']}/{summary['total_servers']}, "
                           f"Interactive: {summary['interactive_capable']}, Testing: {summary['testing_capable']}")
            
            # Check for issues
            if summary['available_servers'] == 0:
                self.log_message("⚠️  WARNING: No MCP servers available!")
            elif summary['interactive_capable'] == 0:
                self.log_message("⚠️  WARNING: No interactive MCP servers available!")
            elif summary['testing_capable'] == 0:
                self.log_message("⚠️  WARNING: No AI testing MCP servers available!")
            else:
                self.log_message("✅ All MCP servers healthy")
            
            return health_results
            
        except Exception as e:
            self.log_message(f"❌ Error during MCP check: {e}")
            return None
    
    def setup_schedule(self):
        """Set up monitoring schedule."""
        # Check every 30 minutes
        schedule.every(30).minutes.do(lambda: asyncio.run(self.run_scheduled_check()))
        
        # Check every hour
        schedule.every().hour.do(lambda: asyncio.run(self.run_scheduled_check()))
        
        # Check every day at 9 AM
        schedule.every().day.at("09:00").do(lambda: asyncio.run(self.run_scheduled_check()))
        
        # Check every Monday at 8 AM (weekly deep check)
        schedule.every().monday.at("08:00").do(lambda: asyncio.run(self.run_weekly_deep_check()))
        
        self.log_message("MCP monitoring schedule configured")
    
    async def run_weekly_deep_check(self):
        """Run a comprehensive weekly check."""
        self.log_message("Starting weekly deep MCP check...")
        
        # Run full health check
        health_results = await self.run_scheduled_check()
        
        if health_results:
            # Generate weekly report
            await self.generate_weekly_report(health_results)
    
    async def generate_weekly_report(self, health_results: Dict):
        """Generate weekly MCP health report."""
        report_file = self.results_dir / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(report_file, 'w') as f:
            f.write("# Weekly MCP Health Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            summary = health_results['summary']
            f.write("## Summary\n\n")
            f.write(f"- **Total Servers**: {summary['total_servers']}\n")
            f.write(f"- **Available Servers**: {summary['available_servers']}\n")
            f.write(f"- **Interactive Capable**: {summary['interactive_capable']}\n")
            f.write(f"- **Testing Capable**: {summary['testing_capable']}\n\n")
            
            # Server details
            f.write("## Server Details\n\n")
            for server_name, server_info in health_results['servers'].items():
                f.write(f"### {server_info['name']}\n")
                f.write(f"- **Available**: {'✅' if server_info['available'] else '❌'}\n")
                f.write(f"- **Interactive Mode**: {'✅' if server_info.get('interactive_tested') else '❌'}\n")
                f.write(f"- **AI Testing**: {'✅' if server_info.get('testing_tested') else '❌'}\n")
                if server_info.get('error'):
                    f.write(f"- **Error**: {server_info['error']}\n")
                f.write("\n")
            
            # Recommendations
            recommendations = self.monitor.generate_recommendations(health_results)
            f.write("## Recommendations\n\n")
            for rec in recommendations:
                f.write(f"- {rec}\n")
        
        self.log_message(f"Weekly report generated: {report_file}")
    
    def run_monitoring(self):
        """Run the monitoring loop."""
        self.log_message("Starting MCP monitoring service...")
        self.setup_schedule()
        
        # Run initial check
        asyncio.run(self.run_scheduled_check())
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function."""
    monitor = ScheduledMCPMonitor()
    
    print("🤖 Scheduled MCP Monitor for Alpha-Gen")
    print("=" * 50)
    print("Press Ctrl+C to stop monitoring")
    
    try:
        monitor.run_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
