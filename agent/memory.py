"""Memory management and context handling."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json

from loguru import logger

from agent.models.task import Task
from agent.models.result import Result


class MemoryManager:
    """
    Manages agent memory, context, and session state.
    """

    def __init__(self, max_memory_size: int = 1000):
        """
        Initialize memory manager.

        Args:
            max_memory_size: Maximum number of items to keep in memory
        """
        self.max_memory_size = max_memory_size
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, Result] = {}
        self.context_stack: deque = deque(maxlen=max_memory_size)
        self.execution_history: List[Dict[str, Any]] = []

    def add_task(self, task: Task) -> None:
        """Add a task to memory."""
        self.tasks[task.id] = task
        self._log_event("task_added", {"task_id": task.id, "description": task.description})

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task from memory."""
        return self.tasks.get(task_id)

    def add_result(self, result: Result) -> None:
        """Add a result to memory."""
        self.results[result.id] = result
        self._log_event("result_added", {"result_id": result.id, "status": result.status.value})

    def get_result(self, result_id: str) -> Optional[Result]:
        """Retrieve a result from memory."""
        return self.results.get(result_id)

    def get_results_for_task(self, task_id: str) -> List[Result]:
        """Get all results for a specific task."""
        return [r for r in self.results.values() if r.task_id == task_id]

    def push_context(self, context: Dict[str, Any]) -> None:
        """Push context onto the stack."""
        self.context_stack.append({
            "timestamp": datetime.now(),
            "context": context,
        })

    def pop_context(self) -> Optional[Dict[str, Any]]:
        """Pop context from the stack."""
        if self.context_stack:
            return self.context_stack.pop()["context"]
        return None

    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """Get current context without popping."""
        if self.context_stack:
            return self.context_stack[-1]["context"]
        return None

    def clear_context_stack(self) -> None:
        """Clear the context stack."""
        self.context_stack.clear()

    def get_execution_history(
        self,
        limit: Optional[int] = None,
        task_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get execution history.

        Args:
            limit: Maximum number of entries to return
            task_id: Filter by specific task

        Returns:
            List of execution history entries
        """
        history = self.execution_history
        if task_id:
            history = [h for h in history if h.get("task_id") == task_id]

        if limit:
            history = history[-limit:]

        return history

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        successful_results = [
            r for r in self.results.values()
            if r.status.value == "success"
        ]

        return {
            "total_tasks": len(self.tasks),
            "total_results": len(self.results),
            "successful_executions": len(successful_results),
            "memory_size": len(self.execution_history),
            "timestamp": datetime.now().isoformat(),
        }

    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event to execution history."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data,
        }
        self.execution_history.append(event)

        if len(self.execution_history) > self.max_memory_size:
            self.execution_history.pop(0)

    def cleanup_old_data(self, days: int = 7) -> None:
        """Remove old data from memory."""
        cutoff_time = datetime.now() - timedelta(days=days)

        logger.info(f"Cleaning up data older than {cutoff_time}")

        # This is a placeholder - in production, would implement proper cleanup
        pass

    def export_session(self) -> Dict[str, Any]:
        """Export current session data."""
        return {
            "summary": self.get_session_summary(),
            "tasks": {k: v.to_dict() for k, v in self.tasks.items()},
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "history": self.execution_history,
        }

    def __repr__(self) -> str:
        return (
            f"MemoryManager(tasks={len(self.tasks)}, "
            f"results={len(self.results)}, "
            f"history={len(self.execution_history)})"
        )
