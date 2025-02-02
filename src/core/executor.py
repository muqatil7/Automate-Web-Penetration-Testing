# cyber_toolkit/core/executor.py
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
from typing import List, Dict
from rich.console import Console
from .progress import DetailedOperationsTracker
from .upload_output_bot import send_file_to_bot

DEFAULT_OUTPUT_DIR = "outputs"
DEFAULT_INSTALL_DIR = "tools_installations"

class ToolExecutor:
    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR, install_dir: str = DEFAULT_INSTALL_DIR):
        self.output_dir = Path(output_dir)
        self.install_dir = Path(install_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.tracker = DetailedOperationsTracker()
        self.console = Console()  # Initialize the console object

    def _run_command(self, command: str, tool: dict, target: str):
        tool_name = tool['name']
        self.tracker.update_operation(
            tool_name,
            "Initializing",
            command
        )
        
        tool_output_dir = self.output_dir / tool['output_dir']
        tool_output_dir.mkdir(exist_ok=True)
        
        log_file = tool_output_dir / f"{target.replace('://', '_').replace('/', '_')}.log"
        tool_path = self.install_dir / tool_name
        
        formatted_command = command.format(target=target)
        
        try:
            self.tracker.update_operation(tool_name, "Running", formatted_command)
            
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    formatted_command,
                    shell=True,
                    cwd=tool_path,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                stdout, stderr = process.communicate()
                
            result = {
                'tool': tool_name,
                'command': formatted_command,
                'exit_code': process.returncode,
                'log_path': str(log_file)
            }
            
            status = "Completed Successfully" if process.returncode == 0 else "Failed"
            self.tracker.update_operation(tool_name, status, formatted_command, result)
            
            return result
            
        except Exception as e:
            error_result = {
                'tool': tool_name,
                'command': formatted_command,
                'exit_code': -1,
                'log_path': str(log_file),
                'error': str(e)
            }
            self.tracker.update_operation(
                tool_name,
                "Execution Error",
                formatted_command,
                error_result
            )
            self.logger.error(f"Failed to execute command {formatted_command} for tool {tool_name}: {str(e)}")
            return error_result

    def run_tools(self, tools: List[Dict], target: str, max_workers: int = 4):
        self.console.print("[bold green]Starting tools execution...[/bold green]")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._run_command, tool['run_command'], tool, target)
                for tool in tools
            ]
            
            results = []
            for future, tool in zip(futures, tools):
                try:
                    results.append(future.result())
                    self.tracker.display_operations()
                except Exception as e:
                    error_result = {
                        'error': str(e),
                        'tool': tool['name'],
                        'exit_code': -1
                    }
                    results.append(error_result)
                    self.tracker.update_operation(
                        tool['name'],
                        "Unexpected Failure",
                        tool['run_command'],
                        error_result
                    )
                    self.logger.error(f"Execution failed for tool {tool['name']} with command {tool['run_command']} on target {target}: {str(e)}")
                    self.tracker.display_operations()
            
            # Display final summary
            summary = self.tracker.get_summary()
            self.console.print("\n[bold]Execution Summary:[/bold]")
            self.console.print(f"Total Operations: {summary['total']}")
            self.console.print(f"Completed: {summary['completed']}")
            self.console.print(f"Failed: {summary['failed']}")
            self.console.print(f"In Progress: {summary['in_progress']}")
            send_file_to_bot()
            return results