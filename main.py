# cyber_toolkit/main.py
import argparse
from pathlib import Path
from typing import List
from src.core.tool_manager import ToolManager
from src.core.executor import ToolExecutor
from src.ui_manager import UIManager
import logging

def setup_logging():
    logging.basicConfig(
        filename='cyber_toolkit.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Cybersecurity Tool Orchestrator")
    parser.add_argument("-t", "--target", required=True, help="Target URL or IP")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("-l", "--list-tools", action="store_true", help="List available tools")
    parser.add_argument("-a", "--all-tools", action="store_true", help="Run all available tools")
    parser.add_argument("tools", nargs="*", help="Specific tools to run")
    
    args = parser.parse_args()
    
    # Initialize components
    tm = ToolManager()
    exe = ToolExecutor()
    ui = UIManager()
    
    # Display banner
    ui.show_banner()
    
    if args.list_tools:
        ui.list_tools(tm.tools)
        return
    
    tools_to_run = []
    if args.all_tools:
        tools_to_run = list(tm.tools.values())
    else:
        for tool_name in args.tools:
            tool = tm.get_tool(tool_name)
            if tool:
                tools_to_run.append(tool)
            else:
                ui.show_error(f"Tool {tool_name} not found")
    
    if not tools_to_run:
        ui.show_error("No tools selected to run!")
        return
    
    # Show scan start information
    ui.show_scan_start(args.target, len(tools_to_run), args.workers)
    
    try:
        # Prepare all tools first
        for tool in tools_to_run:
            tm.prepare_tool(tool['name'])
        
        # Run the tools
        results = exe.run_tools(tools_to_run, args.target, args.workers)
        
        # Display results
        ui.display_results(results)
        
    except KeyboardInterrupt:
        ui.show_error("Scan interrupted by user!")
    except Exception as e:
        ui.show_error(f"Critical error: {str(e)}")
        logging.exception("Critical error occurred")

if __name__ == "__main__":
    main()

    