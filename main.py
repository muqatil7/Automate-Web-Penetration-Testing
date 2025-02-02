# main.py
import logging
from pathlib import Path
from src.config_loader import load_config
from src.input_strategy import CLIInput
from src.core.tool_manager import ToolManager
from src.core.executor import ToolExecutor
from src.ui_manager import UIManager

def setup_logging():
    logging.basicConfig(
        filename='cyber_toolkit.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class CyberToolkit:
    def __init__(self, ui_manager, tool_manager, tool_executor, input_strategy):
        self.ui = ui_manager
        self.tm = tool_manager
        self.exe = tool_executor
        self.input_strategy = input_strategy

    def validate_and_prepare_tools(self, tools_input):
        """Validate and prepare selected tools"""
        tools_to_run = []
        if tools_input:
            for tool_name in tools_input:
                tool = self.tm.get_tool(tool_name)
                if self._is_valid_tool(tool):
                    tools_to_run.append(tool)
                else:
                    self.ui.show_error(f"Tool {tool_name} is missing required information or not found")
        else:
            tools_to_run = list(self.tm.tools.values())
        return tools_to_run
    #
    def _is_valid_tool(self, tool):
        """Check if tool has required attributes"""
        return tool and 'name' in tool and 'command' in tool
    
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
        return True

    def run(self):
        """Main execution flow"""
        self.ui.show_banner()
        parameters = self.input_strategy.get_parameters()

        if parameters.get('list_tools'):
            return self.handle_tool_listing()

        target = parameters.get('target')
        workers = parameters.get('workers')
        tools_input = parameters.get('tools', [])

        tools_to_run = self.validate_and_prepare_tools(tools_input)
        
        if not tools_to_run:
            self.ui.show_error("No tools selected to run!")
            return False

        self.ui.show_scan_start(target, len(tools_to_run), workers)

        try:
            self.prepare_environment(tools_to_run)
            self.execute_tools(tools_to_run, target, workers)
            return True
        except KeyboardInterrupt:
            self.ui.show_error("Scan interrupted by user!")
            return False

if __name__ == "__main__":
    input_strategy = CLIInput() 
    app = CyberToolkit(UIManager(), ToolManager(), ToolExecutor(), input_strategy)
    app.run()