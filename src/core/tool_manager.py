# cyber_toolkit/core/tool_manager.py
import os
import yaml
from pathlib import Path
import subprocess
from typing import Dict, List
from .execution_status import ExecutionStatusManager
class ToolManager:
    def __init__(self, tools_dir: str = "tools", install_dir: str = "tools_installations"):
        self.tools_dir = Path(tools_dir)
        self.install_dir = Path(install_dir)
        self.tools: Dict[str, dict] = {}
        self.load_tools()

    def load_tools(self):
        for yaml_file in self.tools_dir.glob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    tool_data = yaml.safe_load(f)
                    self.tools[tool_data['name']] = tool_data
            except Exception as e:
                print(f"Failed to load {yaml_file}: {e}")

    def get_tool(self, name: str) -> dict:
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in the tool directory.")
        return self.tools[name]

    def is_installed(self, tool: dict) -> bool:
        # التحقق من وجود الأداة في مجلد التثبيت العام
        tool_path = self.install_dir / tool['name']
        return tool_path.exists() and any(tool_path.iterdir())

    def install_tool(self, tool: dict):
        status = ExecutionStatusManager()
        status.operations_now = f"Start Installing {tool['name']}..."
        # إنشاء مجلد التثبيت إذا لم يكن موجوداً
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        # تنفيذ أوامر التثبيت في مجلد التثبيت العام
        for cmd in tool['install']:
            process = subprocess.run(
                cmd,
                shell=True,
                cwd=self.install_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if process.returncode != 0:
                raise Exception(f"Installation failed for command '{cmd}': {process.stderr.decode()}")

    def update_tool(self, tool: dict):
        # تحديث الأداة إذا كانت مستندة على Git
        tool_path = self.install_dir / tool['name']
        if (tool_path / ".git").exists():
            subprocess.run(
                "git pull",
                shell=True,
                cwd=tool_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

    def prepare_tool(self, tool_name: str):

        status = ExecutionStatusManager()

        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        if not self.is_installed(tool):
            print(f"[✳] Installing {tool_name}...")
            status.operations_now = f"Installing {tool_name}..."
            self.install_tool(tool)
            status.operations_now = f"{tool_name} installed successfully."
        else:
            print(f"[✳] Updating {tool_name}...")
            self.update_tool(tool)
            status.operations_now = f"{tool_name} is up to date."
            self.update_tool(tool)
        return tool