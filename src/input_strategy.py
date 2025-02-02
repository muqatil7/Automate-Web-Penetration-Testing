from abc import ABC, abstractmethod

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
