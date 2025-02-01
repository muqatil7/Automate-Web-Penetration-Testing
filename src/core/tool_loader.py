import yaml
import os
from pathlib import Path

def load_tools(tools_dir="tools"):
    tools = []
    for file in Path(tools_dir).glob("*.yaml"):
        with open(file) as f:
            tool_data = yaml.safe_load(f)
            tools.append({
                "name": tool_data["name"],
                "install": tool_data["install"],
                "run_command": tool_data["run_command"],
                "output_dir": tool_data.get("output_dir", "default_output")
            })
    return tools