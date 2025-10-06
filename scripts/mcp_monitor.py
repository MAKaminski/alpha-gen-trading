#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Monitor for Alpha-Gen
Checks availability of MCPs for interactive vs non-interactive modes and AI-based testing.
"""

import asyncio
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class MCPMonitor:
    """Monitor MCP availability and functionality."""
    
    def __init__(self):
        self.mcp_servers = {
            'playwright': {
                'name': 'Playwright MCP Server',
                'command': 'npx @modelcontextprotocol/server-playwright',
                'interactive': True,
                'testing': True
            },
            'selenium': {
                'name': 'Selenium MCP Server', 
                'command': 'npx @modelcontextprotocol/server-selenium',
                'interactive': True,
                'testing': True
            },
            'filesystem': {
                'name': 'Filesystem MCP Server',
                'command': 'npx @modelcontextprotocol/server-filesystem',
                'interactive': False,
                'testing': False
            }
        }
        
        self.results = {}
    
    async def check_mcp_availability(self, server_name: str, config: Dict) -> Dict:
        """Check if an MCP server is available and functional."""
        result = {
            'name': config['name'],
            'available': False,
            'interactive_mode': config['interactive'],
            'testing_capable': config['testing'],
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check if the MCP server package is installed
            check_cmd = ['npm', 'list', '-g', f'@modelcontextprotocol/server-{server_name}']
            process = await asyncio.create_subprocess_exec(
                *check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result['available'] = True
                result['version'] = stdout.decode().strip()
            else:
                result['error'] = f"Package not installed: {stderr.decode()}"
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def test_interactive_mode(self, server_name: str) -> bool:
        """Test if MCP server supports interactive mode."""
        if server_name not in ['playwright', 'selenium']:
            return False
        
        try:
            # Test basic interactive functionality
            test_cmd = ['npx', f'@modelcontextprotocol/server-{server_name}', '--help']
            process = await asyncio.create_subprocess_exec(
                *test_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return process.returncode == 0
        except Exception:
            return False
    
    async def test_ai_testing_capability(self, server_name: str) -> bool:
        """Test if MCP server can be used for AI-based testing."""
        if server_name not in ['playwright', 'selenium']:
            return False
        
        try:
            # Test if server can handle structured commands for AI
            test_commands = [
                '{"method": "initialize", "params": {}}',
                '{"method": "ping", "params": {}}'
            ]
            
            for cmd in test_commands:
                process = await asyncio.create_subprocess_exec(
                    'npx', f'@modelcontextprotocol/server-{server_name}',
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate(input=cmd.encode())
                
                if process.returncode != 0:
                    return False
            
            return True
        except Exception:
            return False
    
    async def run_health_check(self) -> Dict:
        """Run comprehensive health check on all MCP servers."""
        print("🔍 Checking MCP Server Availability...")
        print("=" * 50)
        
        health_results = {
            'timestamp': datetime.now().isoformat(),
            'servers': {},
            'summary': {
                'total_servers': len(self.mcp_servers),
                'available_servers': 0,
                'interactive_capable': 0,
                'testing_capable': 0
            }
        }
        
        for server_name, config in self.mcp_servers.items():
            print(f"\n📡 Checking {config['name']}...")
            
            # Check availability
            availability = await self.check_mcp_availability(server_name, config)
            health_results['servers'][server_name] = availability
            
            if availability['available']:
                health_results['summary']['available_servers'] += 1
                
                # Test interactive mode
                if config['interactive']:
                    interactive_ok = await self.test_interactive_mode(server_name)
                    availability['interactive_tested'] = interactive_ok
                    if interactive_ok:
                        health_results['summary']['interactive_capable'] += 1
                
                # Test AI testing capability
                if config['testing']:
                    testing_ok = await self.test_ai_testing_capability(server_name)
                    availability['testing_tested'] = testing_ok
                    if testing_ok:
                        health_results['summary']['testing_capable'] += 1
                
                print(f"✅ {config['name']} - Available")
                if config['interactive']:
                    print(f"   Interactive Mode: {'✅' if availability.get('interactive_tested') else '❌'}")
                if config['testing']:
                    print(f"   AI Testing: {'✅' if availability.get('testing_tested') else '❌'}")
            else:
                print(f"❌ {config['name']} - Not Available")
                if availability['error']:
                    print(f"   Error: {availability['error']}")
        
        return health_results
    
    def generate_recommendations(self, health_results: Dict) -> List[str]:
        """Generate recommendations based on health check results."""
        recommendations = []
        
        available_count = health_results['summary']['available_servers']
        interactive_count = health_results['summary']['interactive_capable']
        testing_count = health_results['summary']['testing_capable']
        
        if available_count == 0:
            recommendations.append("🚨 No MCP servers available. Install required packages:")
            recommendations.append("   npm install -g @modelcontextprotocol/server-playwright")
            recommendations.append("   npm install -g @modelcontextprotocol/server-selenium")
        
        if interactive_count == 0:
            recommendations.append("⚠️  No interactive MCP servers available.")
            recommendations.append("   This may affect Railway login and other interactive tasks.")
        
        if testing_count == 0:
            recommendations.append("⚠️  No AI testing MCP servers available.")
            recommendations.append("   Consider installing Playwright or Selenium MCP servers.")
        
        if available_count > 0 and interactive_count > 0:
            recommendations.append("✅ Interactive MCPs available for Railway login automation")
        
        if available_count > 0 and testing_count > 0:
            recommendations.append("✅ AI testing MCPs available for automated testing")
        
        return recommendations
    
    async def install_missing_mcps(self) -> bool:
        """Install missing MCP servers."""
        print("\n🔧 Installing missing MCP servers...")
        
        install_commands = [
            ['npm', 'install', '-g', '@modelcontextprotocol/server-playwright'],
            ['npm', 'install', '-g', '@modelcontextprotocol/server-selenium'],
            ['npm', 'install', '-g', '@modelcontextprotocol/server-filesystem']
        ]
        
        success = True
        for cmd in install_commands:
            try:
                print(f"Installing {cmd[-1]}...")
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    print(f"✅ {cmd[-1]} installed successfully")
                else:
                    print(f"❌ Failed to install {cmd[-1]}: {stderr.decode()}")
                    success = False
            except Exception as e:
                print(f"❌ Error installing {cmd[-1]}: {e}")
                success = False
        
        return success

async def main():
    """Main function to run MCP monitoring."""
    monitor = MCPMonitor()
    
    print("🤖 MCP Monitor for Alpha-Gen")
    print("=" * 50)
    
    # Run health check
    health_results = await monitor.run_health_check()
    
    # Generate recommendations
    recommendations = monitor.generate_recommendations(health_results)
    
    print("\n📋 Recommendations:")
    print("=" * 30)
    for rec in recommendations:
        print(rec)
    
    # Save results
    results_file = Path("mcp_health_check.json")
    with open(results_file, 'w') as f:
        json.dump(health_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Ask if user wants to install missing MCPs
    if health_results['summary']['available_servers'] < len(monitor.mcp_servers):
        response = input("\nInstall missing MCP servers? (y/N): ").lower().strip()
        if response == 'y':
            await monitor.install_missing_mcps()

if __name__ == "__main__":
    asyncio.run(main())
