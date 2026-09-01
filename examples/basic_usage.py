"""
Basic usage example of the Powerful AI Agent.
"""

import sys
sys.path.insert(0, "..")

from agent import PowerfulAIAgent


def main():
    """Basic usage example."""
    
    # Initialize the agent
    agent = PowerfulAIAgent(
        model="gpt-4",
        temperature=0.7,
        max_iterations=10,
        verbose=True,
    )

    print(f"Agent initialized: {agent}")
    print(f"Session ID: {agent.session_id}\n")

    # Execute a simple task
    task = "Analyze the structure of a Python project and suggest improvements"
    
    context = {
        "language": "Python",
        "project_size": "medium",
        "main_components": ["core", "tools", "models", "examples"],
    }

    print(f"Executing task: {task}")
    print(f"Context: {context}\n")

    result = agent.execute(
        task=task,
        context=context,
        tools=["code_analysis", "file_operations"],
    )

    # Display results
    print("\n" + "="*50)
    print("EXECUTION RESULT")
    print("="*50)
    print(f"Status: {result.status.value}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"Iterations Used: {result.iterations_used}")
    print(f"Tools Used: {result.tools_used}")

    if result.error_message:
        print(f"Error: {result.error_message}")

    print(f"\nOutput: {result.output}")

    # Get session summary
    print("\n" + "="*50)
    print("SESSION SUMMARY")
    print("="*50)
    summary = agent.get_session_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
