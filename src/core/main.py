import argparse
import os
import importlib
import pkgutil
import sys
from pathlib import Path

# Get the absolute path to the src directory
SRC_DIR = Path(__file__).parent.parent
# Add src directory to Python path
sys.path.append(str(SRC_DIR))

# Now we can import from modules and core properly
from core.display import DisplayManager


class ArgumentParserWithError(argparse.ArgumentParser):
    """Custom ArgumentParser with enhanced error handling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display = DisplayManager()

    def error(self, message):
        """Custom error messages"""
        self.display.show_usage_error(self.format_usage(), message)
        sys.exit(2)

    def print_help(self):
        """Custom help message"""
        self.display.show_help(self.format_help())

def setup_argument_parser():
    """Setup and configure argument parser"""
    parser = ArgumentParserWithError(
        description="Web Pentest Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--url",
        required=True,
        help="Target URL to scan (e.g., https://example.com)"
    )
    
    parser.add_argument(
        "--mode",
        required=True,
        nargs='+',
        help="Specify modules to run. Options:\n" + 
             "  - all: Run all available modules\n" +
             "  - specific modules: e.g., port_scanner ssl_checker"
    )
    
    return parser

def load_modules():
    """
    Dynamically load all modules inside the 'modules' directory.
    
    Returns:
        tuple: (modules dict, module_status list)
    """
    modules = {}
    module_status = []
    
    # Get the modules directory path
    modules_dir = SRC_DIR / "modules"
    
    # Update the package path for pkgutil
    for _, mod_name, _ in pkgutil.iter_modules([str(modules_dir)]):
        if mod_name != 'base':  # Skip the base module
            try:
                module = importlib.import_module(f"modules.{mod_name}")
                if hasattr(module, "run_tool"):
                    modules[mod_name] = module
                    module_status.append({"name": mod_name, "status": "loaded"})
                else:
                    module_status.append({"name": mod_name, "status": "no_run"})
            except Exception as e:
                module_status.append({"name": mod_name, "status": "error", "error": str(e)})
    
    return modules, module_status

def main():
    """
    Main function that initializes the tool, parses arguments, and executes selected modules.
    """
    try:
        # Initialize display manager
        display = DisplayManager()
        display.show_banner()
        
        # Parse arguments
        parser = setup_argument_parser()
        args = parser.parse_args()
        
        # Load modules
        modules, module_status = load_modules()
        display.show_modules_table(module_status)
        
        # Create output directory if it doesn't exist
        output_dir = SRC_DIR.parent / "output"
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
            display.print_success("Created output directory")
        
        # Determine which modules to run
        selected_modules = modules.keys() if "all" in args.mode else args.mode or []
        
        # Run selected modules
        with display.show_progress("Running scans...") as status:
            for mod_name in selected_modules:
                if mod_name in modules:
                    display.print_module_start(mod_name)
                    try:
                        results = modules[mod_name].run_tool(args.url)
                        
                        # Format and display results
                        display.show_results(results, mod_name)
                        
                        # Save results to file
                        output_file = output_dir / f"{mod_name}_results.txt"
                        with open(output_file, "w") as f:
                            if isinstance(results, (dict, list)):
                                f.write(str(results))
                            else:
                                f.write(str(results))
                        
                        display.print_file_saved(str(output_file))
                    except Exception as e:
                        display.print_error(f"Error in {mod_name}: {str(e)}")
        
        display.print_completion()

    except AttributeError as e:
        display = DisplayManager()
        display.show_attribute_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        display.show_interrupt()
        sys.exit(1)
    except Exception as e:
        display.show_critical_error(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()