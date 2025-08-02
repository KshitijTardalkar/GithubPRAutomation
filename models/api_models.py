from pydantic import BaseModel, Field
from models.output_model import Result
from typing import Any,Dict,Optional


class AnalyzePrRequest(BaseModel):
    repo_url: str
    pr_number: int

class TaskCreationResponse(BaseModel):
    status: str = "TASK_STARTED"
    message: str
    task_id: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    # The 'info' field contains our custom state metadata
    # meta: Optional[Dict[str, Any]] = None

class TaskResultModel(BaseModel):
    task_id: str
    status: str
    results: Result

class CachedResultResponse(BaseModel):
    cached: bool
    message: str
    result: Result