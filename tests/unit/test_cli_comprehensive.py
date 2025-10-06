"""Comprehensive tests for CLI module."""
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from alphagen.cli import cli, debug, report, run


class TestCLICommands:
    """Test CLI commands functionality."""

    def test_cli_group_creation(self):
        """Test CLI group creation."""
        assert cli is not None
        assert hasattr(cli, 'commands')

    def test_run_command_help(self):
        """Test run command help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ['run', '--help'])
        assert result.exit_code == 0
        assert "Start the real-time Alpha-Gen service" in result.output

    def test_report_command_help(self):
        """Test report command help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ['report', '--help'])
        assert result.exit_code == 0
        assert "Display daily P/L summary" in result.output

    def test_debug_command_help(self):
        """Test debug command help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ['debug', '--help'])
        assert result.exit_code == 0
        assert "Start the unified debug GUI" in result.output

    @patch('alphagen.cli.run_app')
    def test_run_command_execution(self, mock_run_app):
        """Test run command execution."""
        mock_run_app.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(cli, ['run'])
        
        assert result.exit_code == 0
        mock_run_app.assert_called_once()

    @patch('alphagen.cli.fetch_daily_pnl')
    def test_report_command_without_date(self, mock_fetch_daily_pnl):
        """Test report command without date parameter."""
        # Mock the async function
        mock_data = [
            {
                'trade_date': '2024-01-15',
                'realized_pnl': 150.50,
                'trade_count': 5
            },
            {
                'trade_date': '2024-01-16', 
                'realized_pnl': -75.25,
                'trade_count': 3
            }
        ]
        mock_fetch_daily_pnl.return_value = mock_data
        
        runner = CliRunner()
        result = runner.invoke(cli, ['report'])
        
        assert result.exit_code == 0
        assert "2024-01-15: PnL=150.50 on 5 trades" in result.output
        assert "2024-01-16: PnL=-75.25 on 3 trades" in result.output
        mock_fetch_daily_pnl.assert_called_once_with(None)

    @patch('alphagen.cli.fetch_daily_pnl')
    def test_report_command_with_date(self, mock_fetch_daily_pnl):
        """Test report command with specific date."""
        mock_data = [
            {
                'trade_date': '2024-01-15',
                'realized_pnl': 200.75,
                'trade_count': 8
            }
        ]
        mock_fetch_daily_pnl.return_value = mock_data
        
        runner = CliRunner()
        result = runner.invoke(cli, ['report', '--for-date', '2024-01-15'])
        
        assert result.exit_code == 0
        assert "2024-01-15: PnL=200.75 on 8 trades" in result.output
        mock_fetch_daily_pnl.assert_called_once()

    @patch('alphagen.cli.fetch_daily_pnl')
    def test_report_command_empty_data(self, mock_fetch_daily_pnl):
        """Test report command with empty data."""
        mock_fetch_daily_pnl.return_value = []
        
        runner = CliRunner()
        result = runner.invoke(cli, ['report'])
        
        assert result.exit_code == 0
        assert result.output.strip() == ""  # No output for empty data
        mock_fetch_daily_pnl.assert_called_once_with(None)

    @patch('alphagen.cli.fetch_daily_pnl')
    def test_report_command_with_zero_pnl(self, mock_fetch_daily_pnl):
        """Test report command with zero PnL."""
        mock_data = [
            {
                'trade_date': '2024-01-15',
                'realized_pnl': 0.0,
                'trade_count': 0
            }
        ]
        mock_fetch_daily_pnl.return_value = mock_data
        
        runner = CliRunner()
        result = runner.invoke(cli, ['report'])
        
        assert result.exit_code == 0
        assert "2024-01-15: PnL=0.00 on 0 trades" in result.output

    @patch('alphagen.cli.fetch_daily_pnl')
    def test_report_command_with_negative_pnl(self, mock_fetch_daily_pnl):
        """Test report command with negative PnL."""
        mock_data = [
            {
                'trade_date': '2024-01-15',
                'realized_pnl': -123.45,
                'trade_count': 2
            }
        ]
        mock_fetch_daily_pnl.return_value = mock_data
        
        runner = CliRunner()
        result = runner.invoke(cli, ['report'])
        
        assert result.exit_code == 0
        assert "2024-01-15: PnL=-123.45 on 2 trades" in result.output

    @patch('alphagen.gui.debug_app.main')
    def test_debug_command_execution(self, mock_debug_gui):
        """Test debug command execution."""
        mock_debug_gui.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(cli, ['debug'])
        
        assert result.exit_code == 0
        mock_debug_gui.assert_called_once()

    def test_cli_main_execution(self):
        """Test CLI main execution."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Alpha-Gen management CLI" in result.output

    def test_cli_commands_list(self):
        """Test that all expected commands are available."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "run" in result.output
        assert "report" in result.output
        assert "debug" in result.output

    @patch('alphagen.cli.run_app')
    def test_run_command_async_error_handling(self, mock_run_app):
        """Test run command handles async errors."""
        mock_run_app.side_effect = Exception("Test error")
        
        runner = CliRunner()
        result = runner.invoke(cli, ['run'])
        
        # Should still exit with 0 but the error would be in the output
        assert result.exit_code == 0

    @patch('alphagen.cli.fetch_daily_pnl')
    def test_report_command_async_error_handling(self, mock_fetch_daily_pnl):
        """Test report command handles async errors."""
        mock_fetch_daily_pnl.side_effect = Exception("Database error")
        
        runner = CliRunner()
        result = runner.invoke(cli, ['report'])
        
        # Should still exit with 0 but the error would be in the output
        assert result.exit_code == 0

    @patch('alphagen.gui.debug_app.main')
    def test_debug_command_error_handling(self, mock_debug_gui):
        """Test debug command handles errors."""
        mock_debug_gui.side_effect = Exception("GUI error")
        
        runner = CliRunner()
        result = runner.invoke(cli, ['debug'])
        
        # Should still exit with 0 but the error would be in the output
        assert result.exit_code == 0

    def test_report_command_date_parsing(self):
        """Test report command date parsing."""
        runner = CliRunner()
        result = runner.invoke(cli, ['report', '--for-date', '2024-12-25'])
        
        # Should not error on valid date format
        assert result.exit_code == 0

    def test_report_command_invalid_date(self):
        """Test report command with invalid date format."""
        runner = CliRunner()
        result = runner.invoke(cli, ['report', '--for-date', 'invalid-date'])
        
        # Should error on invalid date format
        assert result.exit_code != 0
        assert "Error" in result.output or "Invalid" in result.output

    @patch('alphagen.cli.fetch_daily_pnl')
    def test_report_command_multiple_days(self, mock_fetch_daily_pnl):
        """Test report command with multiple days of data."""
        mock_data = [
            {'trade_date': '2024-01-15', 'realized_pnl': 100.0, 'trade_count': 2},
            {'trade_date': '2024-01-16', 'realized_pnl': 200.0, 'trade_count': 4},
            {'trade_date': '2024-01-17', 'realized_pnl': 300.0, 'trade_count': 6}
        ]
        mock_fetch_daily_pnl.return_value = mock_data
        
        runner = CliRunner()
        result = runner.invoke(cli, ['report'])
        
        assert result.exit_code == 0
        assert "2024-01-15: PnL=100.00 on 2 trades" in result.output
        assert "2024-01-16: PnL=200.00 on 4 trades" in result.output
        assert "2024-01-17: PnL=300.00 on 6 trades" in result.output

    def test_individual_command_functions(self):
        """Test individual command functions exist and are callable."""
        assert callable(run)
        assert callable(report)
        assert callable(debug)
        assert callable(cli)

    def test_cli_import_structure(self):
        """Test CLI import structure."""
        from alphagen.cli import cli, debug, report, run
        
        # All functions should be importable
        assert cli is not None
        assert debug is not None
        assert report is not None
        assert run is not None

