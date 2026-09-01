"""Task execution engine."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import time
from loguru import logger

from agent.models.task import Task
from agent.models.result import Result, ResultStatus
from agent.planner import ExecutionPlan
from agent.memory import MemoryManager


class TaskExecutor:
    """
    Executes tasks according to planned steps.
    """

    def __init__(self, timeout: int = 300):
        """
        Initialize the task executor.

        Args:
            timeout: Execution timeout in seconds
        """
        self.timeout = timeout
        self.current_task: Optional[Task] = None
        self.start_time: Optional[datetime] = None

    def execute(
        self,
        plan: ExecutionPlan,
        task: Task,
        memory: MemoryManager,
    ) -> Result:
        """
        Execute a task according to the plan.

        Args:
            plan: ExecutionPlan with steps to execute
            task: Task object
            memory: Memory manager for context

        Returns:
            Result object with execution outcome
        """
        self.current_task = task
        self.start_time = datetime.now()

        logger.info(f"Starting execution of task {task.id}")
        logger.info(f"Executing {plan.step_count} steps")

        result = Result(task_id=task.id)
        execution_results = []

        try:
            for step in plan.steps:
                if self._is_timeout():
                    logger.warning("Execution timeout reached")
                    result.status = ResultStatus.FAILED
                    result.error_message = "Execution timeout"
                    break

                logger.info(f"Executing step {step.step_number}: {step.action.value}")

                # Execute the step
                step_result = self._execute_step(step, task, memory)
                execution_results.append(step_result)

                if not step_result.get("success", False):
                    logger.warning(f"Step {step.step_number} failed")
                    if step.step_number > 1:
                        # Can continue if not the first step
                        result.status = ResultStatus.PARTIAL
                    else:
                        result.status = ResultStatus.FAILED
                        break

                result.iterations_used += 1

        except Exception as e:
            logger.error(f"Execution error: {e}")
            result.status = ResultStatus.FAILED
            result.error_message = str(e)

        # Finalize result
        result.output = {
            "steps_executed": result.iterations_used,
            "total_steps": plan.step_count,
            "results": execution_results,
        }
        result.execution_time = (datetime.now() - self.start_time).total_seconds()
        result.tools_used = plan.steps[0].tools_required if plan.steps else []

        logger.info(
            f"Task execution complete. "
            f"Status: {result.status.value}, "
            f"Time: {result.execution_time:.2f}s"
        )

        return result

    def _execute_step(
        self,
        step: Any,
        task: Task,
        memory: MemoryManager,
    ) -> Dict[str, Any]:
        """
        Execute a single plan step.

        Args:
            step: PlanStep to execute
            task: Parent task
            memory: Memory manager

        Returns:
            Step result dictionary
        """
        try:
            # Simulate step execution
            # In production, this would dispatch to the appropriate tool

            step_output = {
                "step": step.step_number,
                "action": step.action.value,
                "description": step.description,
                "result": f"Executed {step.action.value}",
                "success": True,
            }

            logger.debug(f"Step result: {step_output}")
            return step_output

        except Exception as e:
            logger.error(f"Step execution error: {e}")
            return {
                "step": step.step_number,
                "action": step.action.value,
                "success": False,
                "error": str(e),
            }

    def _is_timeout(self) -> bool:
        """Check if execution has timed out."""
        if not self.start_time:
            return False

        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > self.timeout
