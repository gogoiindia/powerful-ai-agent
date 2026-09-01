"""
Powerful AI Agent - A sophisticated multi-tool AI agent framework.

This package provides a complete AI agent implementation with:
- Advanced reasoning and planning
- Tool orchestration and integration
- GitHub API integration
- Code analysis and execution
- Memory and context management
"""

from agent.core import PowerfulAIAgent
from agent.models.task import Task, TaskStatus
from agent.models.result import Result, ResultStatus

__version__ = "1.0.0"
__author__ = "gogoiindia"
__license__ = "MIT"

__all__ = [
    "PowerfulAIAgent",
    "Task",
    "TaskStatus",
    "Result",
    "ResultStatus",
]
