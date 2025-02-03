# src/core/progress.py
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.live import Live
from datetime import datetime
from typing import Dict, List
import threading
import time

class DetailedOperationsTracker:
    def __init__(self):
        self.console = Console()
        self.operations = {}
        self.lock = threading.Lock()
        self.start_times = {}
        
    def create_status_table(self) -> Table:
        table = Table(show_header=True, header_style="bold blue", title="Active Operations Status")
        table.add_column("Tool Name", style="cyan", width=20)
        table.add_column("Status", style="green", width=15)
        table.add_column("Progress", style="yellow", width=10)
        table.add_column("Time Elapsed", style="magenta", width=15)
        table.add_column("CPU Usage", style="blue", width=10)
        table.add_column("Memory", style="blue", width=10)
        return table
    
    def create_details_table(self) -> Table:
        table = Table(show_header=True, header_style="bold green", title="Operation Details")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Command", style="yellow", no_wrap=True)
        table.add_column("Start Time", style="blue")
        table.add_column("Output File", style="magenta")
        table.add_column("Exit Code", style="red")
        table.add_column("Last Error", style="red")
        return table

    def format_time_elapsed(self, start_time: float) -> str:
        elapsed = time.time() - start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_operation(self, tool_name: str, status: str, command: str, result: Dict = None):
        with self.lock:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if tool_name not in self.start_times:
                self.start_times[tool_name] = time.time()
            
            self.operations[tool_name] = {
                "status": status,
                "command": command,
                "start_time": current_time,
                "progress": "100%" if result else "In Progress",
                "time_elapsed": self.format_time_elapsed(self.start_times[tool_name]),
                "cpu_usage": "N/A",  # Could be implemented with psutil
                "memory_usage": "N/A",  # Could be implemented with psutil
                "output_file": result.get('log_path', 'N/A') if result else 'N/A',
                "exit_code": str(result.get('exit_code', 'N/A')) if result else 'N/A',
                "error": str(result.get('error', '')) if result and 'error' in result else ''
            }

    def display_operations(self):
        status_table = self.create_status_table()
        details_table = self.create_details_table()
        
        for tool_name, data in self.operations.items():
            # Add to status table
            status_table.add_row(
                tool_name,
                data["status"],
                data["progress"],
                data["time_elapsed"],
                data["cpu_usage"],
                data["memory_usage"]
            )
            
            # Add to details table
            details_table.add_row(
                tool_name,
                data["command"],
                data["start_time"],
                data["output_file"],
                data["exit_code"],
                data["error"][:50] + "..." if len(data["error"]) > 50 else data["error"]
            )
        
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold yellow]Cyber Toolkit Operations Monitor[/bold yellow]",
            border_style="green"
        ))
        self.console.print()
        self.console.print(status_table)
        self.console.print()
        self.console.print(details_table)
        self.console.print()
        
    def get_summary(self) -> Dict:
        total_ops = len(self.operations)
        completed = sum(1 for op in self.operations.values() if op["status"] == "Completed")
        failed = sum(1 for op in self.operations.values() if "Failed" in op["status"])
        return {
            "total": total_ops,
            "completed": completed,
            "failed": failed,
            "in_progress": total_ops - completed - failed
        }