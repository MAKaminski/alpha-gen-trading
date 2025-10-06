#!/usr/bin/env python3
"""
Setup MCP monitoring and AI-based testing for Alpha-Gen project.
This script configures regular monitoring of MCP availability and functionality.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from datetime import datetime

class MCPSetup:
    """Setup MCP monitoring and testing."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.log_file = self.project_root / "mcp_setup.log"
    
    def log(self, message: str):
        """Log message with timestamp."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        print(f"[{timestamp}] {message}")
    
    async def install_required_packages(self) -> bool:
        """Install required packages for MCP monitoring."""
        self.log("Installing required packages...")
        
        packages = [
            'schedule',
            'asyncio',
            'pathlib'
        ]
        
        success = True
        for package in packages:
            try:
                result = subprocess.run(
                    ['pip', 'install', package],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log(f"✅ {package} installed successfully")
                else:
                    self.log(f"❌ Failed to install {package}: {result.stderr}")
                    success = False
            except Exception as e:
                self.log(f"❌ Error installing {package}: {e}")
                success = False
        
        return success
    
    async def install_mcp_servers(self) -> bool:
        """Install MCP servers."""
        self.log("Installing MCP servers...")
        
        mcp_servers = [
            '@modelcontextprotocol/server-playwright',
            '@modelcontextprotocol/server-selenium',
            '@modelcontextprotocol/server-filesystem'
        ]
        
        success = True
        for server in mcp_servers:
            try:
                result = subprocess.run(
                    ['npm', 'install', '-g', server],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log(f"✅ {server} installed successfully")
                else:
                    self.log(f"❌ Failed to install {server}: {result.stderr}")
                    success = False
            except Exception as e:
                self.log(f"❌ Error installing {server}: {e}")
                success = False
        
        return success
    
    async def setup_cron_jobs(self) -> bool:
        """Set up cron jobs for regular monitoring."""
        self.log("Setting up cron jobs...")
        
        try:
            # Create cron job entries
            cron_entries = [
                "# MCP Monitoring - Every 30 minutes",
                "*/30 * * * * cd /Users/makaminski1337/Developer/alpha-gen && python scripts/mcp_monitor.py >> mcp_monitoring.log 2>&1",
                "",
                "# AI Testing - Every 2 hours",
                "0 */2 * * * cd /Users/makaminski1337/Developer/alpha-gen && python scripts/ai_testing_framework.py >> ai_testing.log 2>&1",
                "",
                "# Weekly Deep Check - Every Monday at 8 AM",
                "0 8 * * 1 cd /Users/makaminski1337/Developer/alpha-gen && python scripts/schedule_mcp_checks.py >> weekly_mcp_check.log 2>&1"
            ]
            
            # Write cron file
            cron_file = self.project_root / "mcp_cron.txt"
            with open(cron_file, 'w') as f:
                f.write("\n".join(cron_entries))
            
            self.log(f"✅ Cron jobs configured in {cron_file}")
            self.log("To activate, run: crontab mcp_cron.txt")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error setting up cron jobs: {e}")
            return False
    
    async def create_monitoring_dashboard(self) -> bool:
        """Create a simple monitoring dashboard."""
        self.log("Creating monitoring dashboard...")
        
        try:
            dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Alpha-Gen MCP Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .healthy { background-color: #d4edda; color: #155724; }
        .warning { background-color: #fff3cd; color: #856404; }
        .error { background-color: #f8d7da; color: #721c24; }
        .refresh { margin: 20px 0; }
        .refresh button { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .refresh button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <h1>Alpha-Gen MCP Monitoring Dashboard</h1>
    
    <div class="refresh">
        <button onclick="location.reload()">Refresh Status</button>
    </div>
    
    <div id="status">
        <div class="status healthy">
            <h3>MCP Monitor</h3>
            <p>Status: Running</p>
            <p>Last Check: <span id="last-check">Loading...</span></p>
        </div>
        
        <div class="status healthy">
            <h3>AI Testing Framework</h3>
            <p>Status: Active</p>
            <p>Last Test: <span id="last-test">Loading...</span></p>
        </div>
        
        <div class="status healthy">
            <h3>Railway Deployment</h3>
            <p>Status: Connected</p>
            <p>URL: <span id="railway-url">Loading...</span></p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setInterval(() => {
            location.reload();
        }, 300000);
        
        // Load status from API (when available)
        fetch('/api/mcp-status')
            .then(response => response.json())
            .then(data => {
                document.getElementById('last-check').textContent = data.lastCheck || 'Unknown';
                document.getElementById('last-test').textContent = data.lastTest || 'Unknown';
                document.getElementById('railway-url').textContent = data.railwayUrl || 'Unknown';
            })
            .catch(error => {
                console.log('Status API not available yet');
            });
    </script>
</body>
</html>
            """
            
            dashboard_file = self.project_root / "mcp_dashboard.html"
            with open(dashboard_file, 'w') as f:
                f.write(dashboard_html)
            
            self.log(f"✅ Monitoring dashboard created: {dashboard_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Error creating dashboard: {e}")
            return False
    
    async def run_initial_check(self) -> bool:
        """Run initial MCP check."""
        self.log("Running initial MCP check...")
        
        try:
            result = subprocess.run(
                ['python', 'scripts/mcp_monitor.py'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("✅ Initial MCP check completed successfully")
                return True
            else:
                self.log(f"❌ Initial MCP check failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error running initial check: {e}")
            return False
    
    async def setup_complete(self) -> bool:
        """Complete MCP setup process."""
        self.log("🚀 Starting MCP setup for Alpha-Gen...")
        
        steps = [
            ("Installing required packages", self.install_required_packages),
            ("Installing MCP servers", self.install_mcp_servers),
            ("Setting up cron jobs", self.setup_cron_jobs),
            ("Creating monitoring dashboard", self.create_monitoring_dashboard),
            ("Running initial check", self.run_initial_check)
        ]
        
        success = True
        for step_name, step_func in steps:
            self.log(f"Step: {step_name}")
            if not await step_func():
                self.log(f"❌ Failed: {step_name}")
                success = False
            else:
                self.log(f"✅ Completed: {step_name}")
        
        if success:
            self.log("🎉 MCP setup completed successfully!")
            self.log("Next steps:")
            self.log("1. Run: crontab mcp_cron.txt")
            self.log("2. Open: mcp_dashboard.html")
            self.log("3. Monitor: mcp_monitoring.log")
        else:
            self.log("❌ MCP setup completed with errors")
        
        return success

async def main():
    """Main function."""
    setup = MCPSetup()
    await setup.setup_complete()

if __name__ == "__main__":
    asyncio.run(main())
