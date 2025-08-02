import json
import os
from fastapi import FastAPI, HTTPException, Depends
from celery.result import AsyncResult

from models.api_models import TaskCreationResponse, CachedResultResponse, AnalyzePrRequest, \
    TaskStatusResponse, TaskResultModel
from models.output_model import Result
from services.github_services.get_pr import GitHubService
from services.redis_services.redis_cache import RedisCacheService
from celery_app import analyze_pr_task
app = FastAPI(title="PR Analysis API")


# --- Dependency Injection for Services ---
# This is a robust way to manage service instances.

def get_github_service():
    token = os.environ.get("GITHUB_API_TOKEN")
    if not token:
        print("GITHUB_API_TOKEN not configured on server.")
    return GitHubService(github_token=token)


def get_result_cache_service():
    # Use DB 3 for the final analysis result cache
    return RedisCacheService(db=3)


# --- API Endpoints ---

@app.post("/analyze-pr", response_model=TaskCreationResponse, responses={200: {"model": CachedResultResponse}})
def start_or_get_analysis(request: AnalyzePrRequest):

    task = analyze_pr_task.delay(request.repo_url, request.pr_number)
    return TaskCreationResponse(
        message="Analysis has been started in the background.",
        task_id=task.id
    )


@app.get("/status/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """
    Retrieves the current status of a background task, including custom progress states.
    """
    task_result = AsyncResult(task_id, app=analyze_pr_task.app)
    if not task_result.state:
        raise HTTPException(status_code=404, detail="Task ID not found.")

    return TaskStatusResponse(
        task_id=task_id,
        status=task_result.state,
    )


@app.get("/result/{task_id}", response_model=TaskResultModel)
def get_task_result(task_id: str):
    """
    Retrieves the final result of a completed and successful task.
    """
    task_result = AsyncResult(task_id, app=analyze_pr_task.app)

    if not task_result.ready():
        raise HTTPException(status_code=404, detail="Task is not yet complete or does not exist.")

    if task_result.failed():
        error_info = task_result.info if isinstance(task_result.info, dict) else {'error': str(task_result.info)}
        raise HTTPException(status_code=500, detail=f"Task failed: {error_info.get('error', 'Unknown error')}")

    parsed_results = Result.parse_obj(task_result.get())

    return TaskResultModel(
        task_id=task_id,
        status=task_result.state,
        results=parsed_results,
    )

