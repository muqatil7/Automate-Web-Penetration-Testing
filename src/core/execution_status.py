# src/core/execution_status.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path
import json

@dataclass
class OperationStatus:
    tool_name: str
    status: str
    command: str
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[Dict] = None

class ExecutionStatusManager:
    def __init__(self, status_file: str = "execution_status.json"):
        self.status_file = Path(status_file)
        self.operations: Dict[str, OperationStatus] = {}
        self.operations_now: str = ""

    def update_operation(self, tool_name: str, status: str, command: str, result: Optional[Dict] = None) -> None:
        """Update the status of an operation"""
        if tool_name not in self.operations:
            self.operations[tool_name] = OperationStatus(
                tool_name=tool_name,
                status=status,
                command=command,
                start_time=datetime.now()
            )
        else:
            self.operations[tool_name].status = status
            if status in ["Successfully", "Failed", "Execution Error"]:
                self.operations[tool_name].end_time = datetime.now()
            self.operations[tool_name].result = result

        self._save_status()

    def get_operation_status(self, tool_name: str) -> Optional[OperationStatus]:
        """Get the status of a specific operation"""
        return self.operations.get(tool_name)

    def get_all_operations(self) -> List[OperationStatus]:
        """Get all operations"""
        return list(self.operations.values())

    def get_summary(self) -> Dict[str, int]:
        """Get execution summary"""
        total = len(self.operations)
        completed = sum(1 for op in self.operations.values()
                       if op.status == "Successfully")
        failed = sum(1 for op in self.operations.values()
                    if op.status in ["Failed", "Execution Error"])
        in_progress = total - (completed + failed)

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress
        }

    def _save_status(self) -> None:
        """Save current status to file"""
        status_data = {
            tool_name: {
                "status": op.status,
                "command": op.command,
                "start_time": op.start_time.isoformat(),
                "end_time": op.end_time.isoformat() if op.end_time else None,
                "result": op.result
            }
            for tool_name, op in self.operations.items()
        }

        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)

    def load_status(self) -> None:
        """Load status from file"""
        if not self.status_file.exists():
            return

        with open(self.status_file, 'r') as f:
            status_data = json.load(f)

        for tool_name, data in status_data.items():
            self.operations[tool_name] = OperationStatus(
                tool_name=tool_name,
                status=data["status"],
                command=data["command"],
                start_time=datetime.fromisoformat(data["start_time"]),
                end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
                result=data["result"]
            )