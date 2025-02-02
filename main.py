# main_app.py
import logging
from pathlib import Path
from src.config_loader import load_config
from src.input_strategy import CLIInput  # يمكن تبديله بـ WebInput أو TelegramInput
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

    def run(self):
        self.ui.show_banner()
        parameters = self.input_strategy.get_parameters()

        if parameters.get('list_tools'):
            self.ui.list_tools(self.tm.tools)
            return

        # يمكن استخدام ملف الإعدادات مع المعطيات من الإدخال
        target = parameters.get('target')
        workers = parameters.get('workers')
        tools_input = parameters.get('tools', [])

        tools_to_run = []
        if tools_input:
            for tool_name in tools_input:
                tool = self.tm.get_tool(tool_name)
                if tool and 'name' in tool and 'command' in tool:
                    tools_to_run.append(tool)
                else:
                    self.ui.show_error(f"Tool {tool_name} is missing required information or not found")
        else:
            tools_to_run = list(self.tm.tools.values())

        if not tools_to_run:
            self.ui.show_error("No tools selected to run!")
            return

        self.ui.show_scan_start(target, len(tools_to_run), workers)

        try:
            for tool in tools_to_run:
                self.tm.prepare_tool(tool['name'])
            results = self.exe.run_tools(tools_to_run, target, workers)
            self.ui.display_results(results)
        except KeyboardInterrupt:
            self.ui.show_error("Scan interrupted by user!")
        except Exception as e:
            self.ui.show_error(f"Critical error: {str(e)}")
            logging.exception("Critical error occurred")

if __name__ == "__main__":
    setup_logging()
    # يمكن اختيار نوع الإدخال المناسب هنا
    input_strategy = CLIInput()
    app = CyberToolkit(UIManager(), ToolManager(), ToolExecutor(), input_strategy)
    app.run()