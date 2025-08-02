from pydantic import BaseModel
from typing import List


class Issue(BaseModel):
    """
    A class to represent an issue found in a file.

    Attributes:
        type (str): The type of issue (e.g., 'bug', 'style').
        line (int): The line number where the issue is located.
        description (str): A brief description of the issue.
        suggestion (str): A suggested fix for the issue.
    """
    type: str
    line: int
    description: str
    suggestion: str


class FileAnalysis(BaseModel):
    """
    A class to represent the analysis of a single file.

    Attributes:
        name (str): The name of the file being analyzed.
        issues (List[Issue]): A list of issues found in the file.
    """
    name: str
    issues: List[Issue]


class Summary(BaseModel):
    """
    A class to represent a summary of the analysis across multiple files.

    Attributes:
        total_files (int): The total number of files analyzed.
        total_issues (int): The total number of issues found across all files.
        critical_issues (int): The number of critical issues found.
    """
    total_files: int
    total_issues: int
    critical_issues: int


class Result(BaseModel):
    """
    A class to represent the overall result of the analysis.

    Attributes:
        files (List[FileAnalysis]): A list of file analyses performed.
        summary (Summary): A summary of the overall findings.
    """
    files: List[FileAnalysis]
    summary: Summary
