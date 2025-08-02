from crewai import Task
from services.ai_services.agent import code_review_agent


# Define a task to analyze submitted code
code_analysis_task = Task(
    description="Analyse submitted Github Pull Request diffs converted to JSON for all possible issues.",
    expected_output=(
        "Analyse diffs for code style and formatting issues, potential bugs or errors, "
        "performance improvements and best practices. Here are the json converted diffs: {code}"
    ),
    agent=code_review_agent,
)