from pathlib import Path
import datetime

class OutputHandler:
    def __init__(self, base_dir="outputs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def _get_output_path(self, tool_name):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        tool_dir = self.base_dir / tool_name
        tool_dir.mkdir(exist_ok=True)
        return tool_dir / f"{timestamp}_results.txt"

    def save_output(self, tool_name, stdout, stderr):
        output_path = self._get_output_path(tool_name)
        with open(output_path, "w") as f:
            f.write("=== STDOUT ===\n")
            f.write(stdout)
            f.write("\n=== STDERR ===\n")
            f.write(stderr)
        return output_path