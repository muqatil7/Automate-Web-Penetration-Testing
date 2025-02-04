# src/app.py
import logging
from pathlib import Path
from src.interfaces.config_loader import load_config
from src.core.tool_manager import ToolManager
from src.core.executor import ToolExecutor
from src.interfaces.ui_manager import UIManager
from src.core.tool_loader import load_tools

def setup_logging():
    logging.basicConfig(
        filename='cyber_toolkit.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class CyberToolkit:
    def __init__(self):
        self.ui = UIManager()
        self.tm = ToolManager()
        self.exe = ToolExecutor()

    def validate_and_prepare_tools(self, tools_input):
        """Validate and prepare selected tools"""
        tools_to_run = []
        if tools_input:
            for tool_name in tools_input:
                tool = self.tm.get_tool(tool_name)
                if self._is_valid_tool(tool):
                    tools_to_run.append(tool)
                else:
                    print(f"Tool {tool_name} is missing required information or not found")
                    self.ui.show_error(f"Tool {tool_name} is missing required information or not found")
        else:
            tools_to_run = list(self.tm.tools.values())
        return tools_to_run
    
    def _is_valid_tool(self, tool_name):
        """Check if tool has required attributes"""
        try:
            if any(tool['name'] == tool_name['name'] for tool in load_tools()):
                return True
        except KeyError as e:
            print("KeyError", e)
            return False
    
    def prepare_environment(self, tools_to_run):
        """Prepare environment for tools execution"""
        for tool in tools_to_run:
            self.tm.prepare_tool(tool['name'])

    def execute_tools(self, tools_to_run, target, workers):
        """Execute tools and handle results"""
        try:
            results = self.exe.run_tools(tools_to_run, target, workers)
            self.ui.display_results(results)
        except Exception as e:
            self._handle_execution_error(e)

    def _handle_execution_error(self, error):
        """Handle execution errors"""
        self.ui.show_error(f"Critical error: {str(error)}")
        logging.exception("Critical error occurred")

    def handle_tool_listing(self):
        """Handle tool listing request"""
        self.ui.list_tools(self.tm.tools)
        return self.tm.tools