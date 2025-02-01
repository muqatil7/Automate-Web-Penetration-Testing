# cyber_toolkit/core/executor.py
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
from typing import List, Dict

class ToolExecutor:
    def __init__(self, output_dir: str = "outputs", install_dir: str = "tools_installations"):
        self.output_dir = Path(output_dir)
        self.install_dir = Path(install_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def _run_command(self, command: str, tool: dict, target: str):
        tool_output_dir = self.output_dir / tool['output_dir']
        tool_output_dir.mkdir(exist_ok=True)
        
        log_file = tool_output_dir / f"{target.replace('://', '_').replace('/', '_')}.log"
        
        # تحديد المسار الصحيح للأداة المثبتة
        tool_path = self.install_dir / tool['name']
        
        # تغيير المسار الحالي إلى مجلد الأداة قبل تنفيذ الأمر
        formatted_command = command.format(target=target)
        
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                formatted_command,
                shell=True,
                cwd=tool_path,  # الانتقال إلى مجلد الأداة
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True
            )
            process.wait()
            
        return {
            'tool': tool['name'],
            'command': formatted_command,
            'exit_code': process.returncode,
            'log_path': str(log_file)
        }

    def run_tools(self, tools: List[Dict], target: str, max_workers: int = 4):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._run_command, tool['run_command'], tool, target)
                for tool in tools
            ]
            
            results = []
            for future in futures:
                try:
                    results.append(future.result())
                except Exception as e:
                    self.logger.error(f"Execution failed: {str(e)}")
                    results.append({
                        'error': str(e),
                        'tool': 'unknown',
                        'exit_code': -1
                    })
            return results