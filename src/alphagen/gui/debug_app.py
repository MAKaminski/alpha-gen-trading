"""GUI Debug Application for Alpha-Gen."""
from __future__ import annotations

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional

import structlog

from alphagen.core.events import EquityTick, NormalizedTick, OptionQuote, Signal
from alphagen.market_data.base import StreamCallbacks
from alphagen.visualization.simple_gui_chart import SimpleGUChart
from alphagen.etl.normalizer import Normalizer


class DebugGUI:
    """GUI Debug Application with streaming data and chart controls."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Alpha-Gen Debug Console")
        self.root.geometry("1200x800")
        
        self.logger = structlog.get_logger("alphagen.gui.debug")
        
        # State variables
        self.stream_data_active = tk.BooleanVar(value=False)
        self.view_chart_active = tk.BooleanVar(value=False)
        
        # Components
        self.gui_chart: Optional[SimpleGUChart] = None
        self.console_text: Optional[scrolledtext.ScrolledText] = None
        self.normalizer: Optional[Normalizer] = None
        
        # Async event loop
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.app_task: Optional[asyncio.Task] = None
        
        self._setup_ui()
        self._setup_async_loop()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Alpha-Gen Debug Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Stream Data checkbox
        stream_check = ttk.Checkbutton(
            control_frame,
            text="Stream Data",
            variable=self.stream_data_active,
            command=self._on_stream_toggle
        )
        stream_check.grid(row=0, column=0, padx=(0, 20))
        
        # View Chart checkbox
        chart_check = ttk.Checkbutton(
            control_frame,
            text="View Chart",
            variable=self.view_chart_active,
            command=self._on_chart_toggle
        )
        chart_check.grid(row=0, column=1, padx=(0, 20))
        
        # Time scale controls
        ttk.Label(control_frame, text="Time Scale:").grid(row=0, column=2, padx=(20, 5))
        self.time_scale = tk.StringVar(value="1min")
        scale_combo = ttk.Combobox(
            control_frame,
            textvariable=self.time_scale,
            values=["1min", "5min", "15min", "1hour", "4hour", "1day"],
            state="readonly",
            width=8
        )
        scale_combo.grid(row=0, column=3, padx=(5, 10))
        scale_combo.bind("<<ComboboxSelected>>", self._on_time_scale_change)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Stopped")
        self.status_label.grid(row=0, column=4, padx=(20, 0))
        
        # Quick actions frame
        actions_frame = ttk.Frame(control_frame)
        actions_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # OAuth setup button
        oauth_btn = ttk.Button(
            actions_frame,
            text="Setup OAuth",
            command=self._setup_oauth
        )
        oauth_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Clear console button
        clear_btn = ttk.Button(
            actions_frame,
            text="Clear Console",
            command=self._clear_console
        )
        clear_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Export logs button
        export_btn = ttk.Button(
            actions_frame,
            text="Export Logs",
            command=self._export_logs
        )
        export_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Chart frame
        self.chart_frame = ttk.LabelFrame(main_frame, text="Live Chart", padding="5")
        self.chart_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.chart_frame.columnconfigure(0, weight=1)
        self.chart_frame.rowconfigure(0, weight=1)
        
        # Console frame
        console_frame = ttk.LabelFrame(main_frame, text="Console Output", padding="5")
        console_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        # Console text widget
        self.console_text = scrolledtext.ScrolledText(
            console_frame,
            height=15,
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for different log levels
        self.console_text.tag_configure("info", foreground="black")
        self.console_text.tag_configure("warning", foreground="orange")
        self.console_text.tag_configure("error", foreground="red")
        self.console_text.tag_configure("debug", foreground="gray")
        
    def _setup_async_loop(self):
        """Set up the async event loop in a separate thread."""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
            
        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
        
    def _log_to_console(self, message: str, level: str = "info"):
        """Log a message to the console."""
        if not self.console_text:
            return
            
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, f"[{level.upper()}] {message}\n", level)
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)
        
    def _on_stream_toggle(self):
        """Handle stream data checkbox toggle."""
        if self.stream_data_active.get():
            self._log_to_console("Starting data stream...", "info")
            self._start_streaming()
        else:
            self._log_to_console("Stopping data stream...", "info")
            self._stop_streaming()
            
    def _on_chart_toggle(self):
        """Handle view chart checkbox toggle."""
        if self.view_chart_active.get():
            self._log_to_console("Starting live chart...", "info")
            self._start_chart()
        else:
            self._log_to_console("Stopping live chart...", "info")
            self._stop_chart()
            
    def _on_time_scale_change(self, event=None):
        """Handle time scale change."""
        scale = self.time_scale.get()
        self._log_to_console(f"Time scale changed to: {scale}", "info")
        if self.gui_chart:
            self.gui_chart.set_time_scale(scale)
            
    def _start_streaming(self):
        """Start the data streaming."""
        if self.loop and not self.app_task:
            self.app_task = asyncio.run_coroutine_threadsafe(
                self._run_app(), self.loop
            )
            self.status_label.config(text="Status: Streaming")
            
    def _stop_streaming(self):
        """Stop the data streaming."""
        if self.app_task:
            self.app_task.cancel()
            self.app_task = None
            self.status_label.config(text="Status: Stopped")
            
    def _start_chart(self):
        """Start the live chart."""
        if not self.gui_chart:
            # Create embedded chart in the GUI
            self.gui_chart = SimpleGUChart(self.chart_frame)
            # Set initial time scale
            self.gui_chart.set_time_scale(self.time_scale.get())
            self._log_to_console("Live chart created", "info")
        
        # Always initialize normalizer when showing chart
        if not self.normalizer:
            self.normalizer = Normalizer(emit=self._handle_normalized_tick)
            self._log_to_console("Normalizer initialized", "info")
        
        # Show the chart
        self.gui_chart.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._log_to_console("Live chart shown", "info")
            
    def _stop_chart(self):
        """Stop the live chart."""
        if self.gui_chart:
            # Hide the chart instead of destroying it
            self.gui_chart.canvas.get_tk_widget().pack_forget()
            # Don't destroy normalizer, just hide chart
            self._log_to_console("Live chart hidden", "info")
            
    async def _run_app(self):
        """Run the Alpha-Gen application."""
        try:
            from alphagen.app import AlphaGenApp
            
            app = AlphaGenApp()
            
            # Note: We're using embedded chart instead of overriding app._chart
                
            # Set up custom callbacks for console logging
            callbacks = StreamCallbacks(
                on_equity_tick=self._create_async_callback(self._handle_equity_tick),
                on_option_quote=self._create_async_callback(self._handle_option_quote),
                on_error=self._create_async_callback(self._handle_stream_error),
            )
            
            # Start market data provider
            await app._market_data.start(callbacks)
            
            # Keep running until cancelled
            while True:
                await asyncio.sleep(1)
            
        except asyncio.CancelledError:
            self._log_to_console("App stopped", "info")
        except Exception as e:
            self._log_to_console(f"Error running app: {e}", "error")
            self.logger.error("debug_app_error", error=str(e))
            
    async def _handle_equity_tick(self, tick: EquityTick):
        """Handle equity tick data."""
        self._log_to_console(f"Equity: {tick.symbol} = ${tick.price:.2f}", "info")
        
        # Feed to normalizer if chart is active
        if self.normalizer:
            await self.normalizer.ingest_equity(tick)
        
    async def _handle_option_quote(self, quote: OptionQuote):
        """Handle option quote data."""
        self._log_to_console(f"Option: {quote.option_symbol} bid=${quote.bid:.2f} ask=${quote.ask:.2f}", "info")
        
        # Feed to normalizer if chart is active
        if self.normalizer:
            await self.normalizer.ingest_option(quote)
            
    async def _handle_normalized_tick(self, tick: NormalizedTick):
        """Handle normalized tick data for charting."""
        self._log_to_console(f"Normalized tick: VWAP={tick.equity.session_vwap:.2f}, MA9={tick.equity.ma9:.2f}", "debug")
        if self.gui_chart:
            self.gui_chart.handle_tick(tick)
            self._log_to_console("Chart updated with new data", "debug")
            
    async def _handle_stream_error(self, error: Exception):
        """Handle stream errors."""
        error_msg = str(error)
        if "token_invalid" in error_msg or "InvalidTokenError" in error_msg:
            self._log_to_console("❌ OAuth token is invalid or expired!", "error")
            self._log_to_console("Please click 'Setup OAuth' to re-authenticate", "warning")
            # Stop streaming on token error
            if self.stream_data_active.get():
                self.stream_data_active.set(False)
                self._stop_streaming()
        else:
            self._log_to_console(f"Stream error: {error}", "error")
        
    def _create_async_callback(self, async_func):
        """Create an async callback that can be awaited."""
        async def callback_wrapper(*args, **kwargs):
            try:
                await async_func(*args, **kwargs)
            except Exception as e:
                self._log_to_console(f"Callback error: {e}", "error")
        return callback_wrapper
        
    def run(self):
        """Run the GUI application."""
        self._log_to_console("🚀 Alpha-Gen Unified Debug Console started", "info")
        self._log_to_console("", "info")
        self._log_to_console("📊 Features:", "info")
        self._log_to_console("  • Check 'Stream Data' to start receiving live market data", "info")
        self._log_to_console("  • Check 'View Chart' to display live charts", "info")
        self._log_to_console("  • Use 'Setup OAuth' to configure Schwab API access", "info")
        self._log_to_console("  • Use 'Clear Console' to clear the output", "info")
        self._log_to_console("  • Use 'Export Logs' to save console output to file", "info")
        self._log_to_console("", "info")
        self._log_to_console("Ready for debugging! 🐛", "info")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._log_to_console("Application interrupted by user", "warning")
        finally:
            self._cleanup()
            
    def _setup_oauth(self):
        """Setup OAuth for Schwab API."""
        self._log_to_console("Starting OAuth setup...", "info")
        try:
            import subprocess
            import sys
            from pathlib import Path
            
            # Run the OAuth setup script
            script_path = Path(__file__).parent.parent.parent / "scripts" / "setup" / "setup_schwab_oauth.py"
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self._log_to_console("✅ OAuth setup completed successfully!", "info")
            else:
                self._log_to_console(f"❌ OAuth setup failed: {result.stderr}", "error")
                
        except Exception as e:
            self._log_to_console(f"❌ OAuth setup error: {e}", "error")
            
    def _clear_console(self):
        """Clear the console output."""
        if self.console_text:
            self.console_text.config(state=tk.NORMAL)
            self.console_text.delete(1.0, tk.END)
            self.console_text.config(state=tk.DISABLED)
            self._log_to_console("Console cleared", "info")
            
    def _export_logs(self):
        """Export console logs to file."""
        if not self.console_text:
            return
            
        try:
            from tkinter import filedialog
            from datetime import datetime
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=f"alphagen_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.console_text.get(1.0, tk.END))
                self._log_to_console(f"Logs exported to: {filename}", "info")
                
        except Exception as e:
            self._log_to_console(f"Export failed: {e}", "error")

    def _cleanup(self):
        """Clean up resources."""
        if self.app_task:
            self.app_task.cancel()
        # Clean up charts and normalizer
        if self.gui_chart:
            self.gui_chart.clear()
        self.normalizer = None
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)


def main():
    """Main entry point for the debug GUI."""
    app = DebugGUI()
    app.run()


if __name__ == "__main__":
    main()
