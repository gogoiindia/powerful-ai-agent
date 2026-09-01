"""Task planning and reasoning module."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

import openai
from loguru import logger

from agent.models.task import Task


class ActionType(str, Enum):
    """Types of actions the agent can take."""
    ANALYZE = "analyze"
    SEARCH = "search"
    EXECUTE = "execute"
    CREATE = "create"
    MODIFY = "modify"
    VALIDATE = "validate"
    REPORT = "report"


@dataclass
class PlanStep:
    """A single step in an execution plan."""
    step_number: int
    action: ActionType
    description: str
    tools_required: List[str]
    expected_output: str
    dependencies: List[int] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ExecutionPlan:
    """A complete execution plan for a task."""
    task_id: str
    steps: List[PlanStep]
    total_estimated_time: float
    risk_level: str
    validation_strategy: str

    @property
    def step_count(self) -> int:
        return len(self.steps)


class TaskPlanner:
    """
    Intelligent task planner that decomposes complex tasks into executable steps.
    """

    def __init__(self, model: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize the task planner.

        Args:
            model: LLM model to use for planning
            temperature: Sampling temperature
        """
        self.model = model
        self.temperature = temperature

    def plan(self, task: Task) -> ExecutionPlan:
        """
        Create an execution plan for a task.

        Args:
            task: Task to plan

        Returns:
            ExecutionPlan with structured steps
        """
        logger.info(f"Creating plan for task: {task.description}")

        # Generate plan using LLM
        plan_prompt = self._create_planning_prompt(task)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_planner_system_prompt(),
                    },
                    {"role": "user", "content": plan_prompt},
                ],
                temperature=self.temperature,
                max_tokens=2000,
            )

            plan_text = response.choices[0].message.content
            steps = self._parse_plan(plan_text, task.available_tools)

        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            # Fallback to simple plan
            steps = self._create_fallback_plan(task)

        return ExecutionPlan(
            task_id=task.id,
            steps=steps,
            total_estimated_time=sum(self._estimate_step_time(s) for s in steps),
            risk_level=self._assess_risk(task, steps),
            validation_strategy="comprehensive",
        )

    def _create_planning_prompt(self, task: Task) -> str:
        """Create a prompt for task planning."""
        context_str = "\n".join(
            f"- {k}: {v}" for k, v in task.context.items()
        ) if task.context else "None"

        return f"""
Task: {task.description}

Context:
{context_str}

Available Tools:
{', '.join(task.available_tools)}

Please create a detailed execution plan with these steps:
1. Identify the main objective
2. Break down into sub-tasks
3. Define dependencies
4. Specify required tools for each step
5. Estimate time and complexity

Format each step as: [STEP N] Action: Description | Tools: [list] | Dependencies: [list]
"""

    def _get_planner_system_prompt(self) -> str:
        """Get the system prompt for the planner."""
        return """You are an expert task planner. Your job is to:
1. Understand complex tasks
2. Break them down into manageable steps
3. Identify tool requirements
4. Detect dependencies between steps
5. Estimate execution time and complexity

Always be specific and actionable in your plans."""

    def _parse_plan(
        self, plan_text: str, available_tools: List[str]
    ) -> List[PlanStep]:
        """Parse plan text into structured steps."""
        steps = []
        step_number = 1

        # Simple parsing logic - in production, this would be more sophisticated
        lines = plan_text.split("\n")
        for line in lines:
            if "STEP" in line.upper():
                step = PlanStep(
                    step_number=step_number,
                    action=ActionType.ANALYZE,
                    description=line.strip(),
                    tools_required=available_tools[:1],
                    expected_output="Analysis results",
                )
                steps.append(step)
                step_number += 1

        return steps if steps else [self._create_default_step()]

    def _create_fallback_plan(self, task: Task) -> List[PlanStep]:
        """Create a fallback plan when LLM planning fails."""
        return [
            PlanStep(
                step_number=1,
                action=ActionType.ANALYZE,
                description=f"Analyze: {task.description}",
                tools_required=task.available_tools,
                expected_output="Analysis complete",
            ),
            PlanStep(
                step_number=2,
                action=ActionType.EXECUTE,
                description="Execute main task",
                tools_required=task.available_tools,
                expected_output="Task executed",
            ),
        ]

    def _create_default_step(self) -> PlanStep:
        """Create a default step."""
        return PlanStep(
            step_number=1,
            action=ActionType.EXECUTE,
            description="Execute task",
            tools_required=[],
            expected_output="Task completed",
        )

    def _estimate_step_time(self, step: PlanStep) -> float:
        """Estimate execution time for a step."""
        action_times = {
            ActionType.ANALYZE: 30,
            ActionType.SEARCH: 20,
            ActionType.EXECUTE: 60,
            ActionType.CREATE: 120,
            ActionType.MODIFY: 90,
            ActionType.VALIDATE: 30,
            ActionType.REPORT: 15,
        }
        return action_times.get(step.action, 30)

    def _assess_risk(self, task: Task, steps: List[PlanStep]) -> str:
        """Assess the risk level of a task."""
        if len(steps) <= 2:
            return "low"
        elif len(steps) <= 5:
            return "medium"
        else:
            return "high"
