"""Task data models."""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """Represents a task to be executed by the agent."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    context: Dict[str, Any] = Field(default_factory=dict)
    available_tools: List[str] = Field(default_factory=list)
    max_iterations: int = 10
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        data = self.dict()
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data
