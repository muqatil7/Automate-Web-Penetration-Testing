# src/interfaces/ui_manager.py
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box
from typing import List, Dict
import platform
import getpass
from datetime import datetime


class UIManager:
    def __init__(self):
        self.console = Console()
        self.version = "1.0.0"

    def _get_system_info(self):
        """Get basic system information"""
        return {
            "OS": platform.system(),
            "User": getpass.getuser(),
            "Python": platform.python_version()
        }

    def show_banner(self):
        """Display an enhanced styled banner"""
        banner_text = """
        [bold cyan]╔══════════════════════════════════════════╗
        ║     [bold red]Web Pentest Automation Tool[/bold red]          ║
        ║        [yellow]Security Assessment Suite[/yellow]         ║
        ╚══════════════════════════════════════════╝[/bold cyan]
        """
        sys_info = self._get_system_info()
        info_text = f"""[white]
        [bold blue]System Information:[/bold blue]
        • OS: [green]{sys_info['OS']}[/green]
        • User: [green]{sys_info['User']}[/green]
        • Python: [green]{sys_info['Python']}[/green]
        • Time: [green]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/green]
        [bold blue]Tool Information:[/bold blue]
        • Version: [green]{self.version}[/green]
        • Mode: [green]Security Assessment[/green]
        • Status: [green]Active[/green]
        [/white]"""
        warning_text = """[bold yellow]
        ⚠ WARNING: Use this tool responsibly and only on authorized targets.
        All activities are logged and monitored.[/bold yellow]
        """
        self.console.clear()
        self.console.print(Align.center(banner_text))
        self.console.print(Panel(info_text, border_style="blue", title="[white]Session Information[/white]", title_align="center"))
        self.console.print(Panel(warning_text, border_style="yellow", title="[white]Security Notice[/white]", title_align="center"))
        self.console.print("\n")

    def display_results(self, results: List[Dict]):
        """Display scan results in a table"""
        table = Table(title="Scan Results", show_lines=True)
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Exit Code", style="green")
        table.add_column("Log Path", style="yellow")

        for result in results:
            status = "✅ Success" if result.get('exit_code') == 0 else "❌ Failed"
            error = result.get('error', '')
            tool_name = result.get('tool', 'unknown')
            
            if error:
                status += f"\n[red]{error}[/red]"
                
            table.add_row(
                tool_name,
                status,
                str(result.get('exit_code', 'N/A')),
                result.get('log_path', 'N/A')
            )
        
        self.console.print(Panel(table, title="Final Results", border_style="blue"))

    def list_tools(self, tools: Dict[str, Dict]):
        """Display a table of available tools"""
        table = Table(title="Available Tools")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="magenta")
        for name, tool in tools.items():
            table.add_row(name, tool['description'])
        self.console.print(Panel(table, title="Available Tools", border_style="green"))

    def show_error(self, message: str):
        """Display an error message"""
        self.console.print(f"[red]Error: {message}[/red]")

    def show_warning(self, message: str):
        """Display a warning message"""
        self.console.print(f"[yellow]Warning: {message}[/yellow]")

    def show_success(self, message: str):
        """Display a success message"""
        self.console.print(f"[green]Success: {message}[/green]")

    def show_scan_start(self, target: str, num_tools: int, workers: int):
        """Display scan start information"""
        self.console.print(f"\n[bold green]Starting scan for {target}[/bold green]")
        self.console.print(f"[yellow]Running {num_tools} tools with {workers} workers[/yellow]\n")