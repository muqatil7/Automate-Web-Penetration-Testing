from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich import box
from datetime import datetime
from contextlib import contextmanager
import platform
import getpass

class DisplayManager:
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
        try:
            # Create the main banner text
            banner_text = """
            [bold cyan]╔══════════════════════════════════════════╗
            ║     [bold red]Web Pentest Automation Tool[/bold red]          ║
            ║        [yellow]Security Assessment Suite[/yellow]         ║
            ╚══════════════════════════════════════════╝[/bold cyan]
            """
            
            # Create the information panel
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
            
            # Create warning message
            warning_text = """[bold yellow]
            ⚠ WARNING: Use this tool responsibly and only on authorized targets.
            All activities are logged and monitored.[/bold yellow]
            """
            
            # Display the complete banner
            self.console.clear()
            self.console.print(Align.center(banner_text))
            self.console.print(Panel(info_text, 
                                   border_style="blue", 
                                   title="[white]Session Information[/white]", 
                                   title_align="center"))
            self.console.print(Panel(warning_text, 
                                   border_style="yellow", 
                                   title="[white]Security Notice[/white]", 
                                   title_align="center"))
            self.console.print("\n")
            
        except Exception as e:
            self.show_critical_error(f"Error displaying banner: {str(e)}")

    def show_modules_table(self, module_status):
        """Display table of loaded modules"""
        table = Table(title="Available Modules")
        table.add_column("Module Name", style="cyan")
        table.add_column("Status", style="green")
        
        for mod in module_status:
            name = mod["name"]
            if mod["status"] == "loaded":
                status = "✓ Loaded"
            elif mod["status"] == "no_run":
                status = "[yellow]⚠ No run() method[/yellow]"
            else:
                status = f"[red]✗ Error: {mod.get('error', 'Unknown error')}[/red]"
            table.add_row(name, status)
        
        self.console.print(table)
        self.console.print("\n")

    def show_results(self, results, mod_name):
        """Format and display results"""
        if isinstance(results, dict):
            table = Table(title=f"Results from {mod_name}", 
                         show_header=True, header_style="bold magenta")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in results.items():
                table.add_row(str(key), str(value))
            self.console.print(table)
        elif isinstance(results, list):
            panel = Panel("\n".join([f"[cyan]{i+1}.[/cyan] {item}" 
                                   for i, item in enumerate(results)]),
                         title=f"Results from {mod_name}",
                         border_style="magenta")
            self.console.print(panel)
        else:
            panel = Panel(str(results), 
                         title=f"Results from {mod_name}", 
                         border_style="magenta")
            self.console.print(panel)

    def show_usage_error(self, usage, message):
        """Display usage error"""
        self.console.print("\n")
        self.console.print(Panel(
            Text.assemble(
                ("ERROR", "bold red"),
                "\n\n",
                (message, "yellow"),
                "\n\n",
                ("Correct Usage:", "bold cyan"),
                "\n",
                (usage, "green"),
                "\n",
                ("For more details, use: ", "bold white"),
                ("python main.py --help", "cyan underline")
            ),
            title="[bold red]Invalid Usage[/bold red]",
            border_style="red",
            box=box.DOUBLE,
            padding=(1, 2)
        ))
        self.console.print("\n")

    def show_help(self, help_text):
        """Display help message"""
        self.console.print("\n")
        self.console.print(Panel(
            help_text,
            title="[bold cyan]Help & Usage Guide[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        ))
        self.console.print("\n")

    def show_critical_error(self, error_message):
        """Display critical error message"""
        self.console.print("\n")
        self.console.print(Panel(
            Text.assemble(
                ("Critical Error Occurred\n\n", "bold red"),
                (str(error_message), "yellow"),
                "\n\nTraceback information has been logged."
            ),
            title="[bold red]Error[/bold red]",
            border_style="red",
            box=box.DOUBLE,
            padding=(1, 2)
        ))
        self.console.print("\n")

    def show_attribute_error(self, error_message):
        """Display attribute error message"""
        self.console.print(Panel(
            Text.assemble(
                ("Development Error\n\n", "bold red"),
                ("A required component is missing:\n", "yellow"),
                (str(error_message), "white"),
                "\n\n",
                ("Please report this issue to the development team.", "cyan")
            ),
            title="[bold red]Missing Component Error[/bold red]",
            border_style="red",
            box=box.DOUBLE,
            padding=(1, 2)
        ))

    def show_interrupt(self):
        """Display interrupt message"""
        self.console.print("\n")
        self.console.print(Panel(
            "[yellow]Program execution interrupted by user[/yellow]",
            title="[bold yellow]Interrupted[/bold yellow]",
            border_style="yellow",
            box=box.DOUBLE
        ))
        self.console.print("\n")

    @contextmanager
    def show_progress(self, message):
        """Context manager for showing progress"""
        with self.console.status(f"[bold green]{message}[/bold green]") as status:
            yield status

    def print_module_start(self, mod_name):
        """Print module start message"""
        self.console.print(f"\n[bold blue]Running {mod_name}...[/bold blue]")

    def print_success(self, message):
        """Print success message"""
        self.console.print(f"[green]{message}[/green]")

    def print_error(self, message):
        """Print error message"""
        self.console.print(f"[red]{message}[/red]")

    def print_file_saved(self, filepath):
        """Print file saved message"""
        self.console.print(f"[green]Results saved to {filepath}[/green]")

    def print_completion(self):
        """Print completion message"""
        self.console.print("\n[bold green]✓ All scans completed![/bold green]")