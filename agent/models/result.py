"""Result data models."""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class ResultStatus(str, Enum):
    """Result status."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Result(BaseModel):
    """Represents the result of task execution."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_id: str
    status: ResultStatus = ResultStatus.SUCCESS
    output: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time: float = 0.0
    iterations_used: int = 0
    tools_used: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        data = self.dict()
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        return data

    @property
    def is_success(self) -> bool:
        """Check if result is successful."""
        return self.status == ResultStatus.SUCCESS
