from abc import ABC, abstractmethod
from src.interfaces.ui_manager import UIManager
from src.app import CyberToolkit

class InputStrategy(ABC):
    @abstractmethod
    def get_parameters(self):
        pass

class CLIInput(InputStrategy):
    def get_parameters(self):
        import argparse
        parser = argparse.ArgumentParser(description="Cybersecurity Tool Orchestrator")
        parser.add_argument("-t", "--target", required=True, help="Target URL or IP")
        parser.add_argument("-w", "--workers", type=int, default=4, help="Number of parallel workers")
        parser.add_argument("-l", "--list-tools", action="store_true", help="List available tools")
        parser.add_argument("-a", "--all-tools", action="store_true", help="Run all available tools")
        parser.add_argument("tools", nargs="*", help="Specific tools to run")
        parser.add_argument("--version", action="version", version="Cybersecurity Toolkit v0.1")
        # يمكن إضافة معطيات أخرى مثل بوت تلغرام هنا
        args = parser.parse_args()
        return vars(args)  # إرجاع المعطيات على شكل قاموس

    def __init__(self):
        self.ui = UIManager()
        self.main_function = CyberToolkit()

    def run(self):
        self.ui.show_banner()
        parameters = self.get_parameters()

        if parameters.get('list_tools'):
            return self.main_function.handle_tool_listing()

        target = parameters.get('target')
        workers = parameters.get('workers')
        tools_input = parameters.get('tools', [])

        tools_to_run = self.main_function.validate_and_prepare_tools(tools_input)
        
        if not tools_to_run:
            self.ui.show_error("No tools selected to run!")
            return False

        self.ui.show_scan_start(target, len(tools_to_run), workers)

        try:
            self.main_function.prepare_environment(tools_to_run)
            self.main_function.execute_tools(tools_to_run, target, workers)
            return True
        except KeyboardInterrupt:
            self.ui.show_error("Scan interrupted by user!")
            return False
        

if __name__ == "__main__":
    input_strategy = CLIInput() 
    input_strategy.run()