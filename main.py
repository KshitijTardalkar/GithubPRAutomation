from typing import Union

from fastapi import FastAPI, HTTPException, Depends
from celery.result import AsyncResult
from logger import AppLogger
from models.api_models import TaskCreationResponse, CachedResultResponse, AnalyzePrRequest, \
    TaskStatusResponse, TaskResultModel
from models.output_model import Result
from services.github_services.get_pr import GitHubService
from services.redis_services.redis_cache import RedisCacheService
from celery_app import analyze_pr_task

import os

app = FastAPI(title="PR Analysis API")

# --- Shared Services ---
logger = AppLogger(name="PR Analysis API")

def app_logger_service():
    return logger

def get_github_service():
    token = os.environ.get("GITHUB_API_TOKEN")
    if not token:
        logger.warning("GITHUB_API_TOKEN environment variable not set")
    return GitHubService(github_token=token)

def get_result_cache_service():
    return RedisCacheService(db=2)

# --- API Endpoints ---
@app.post("/analyze-pr", response_model=Union[TaskCreationResponse, CachedResultResponse])
def start_or_get_analysis(
    request: AnalyzePrRequest,
    cache: RedisCacheService = Depends(get_result_cache_service),
    gh: GitHubService = Depends(get_github_service),
    l: AppLogger = Depends(app_logger_service)
):
    request_sha = gh.get_pr_head_sha(request.repo_url, request.pr_number)
    cache_key = f"analysis:{request.repo_url}:{request.pr_number}:{request_sha}"

    cached_json = cache.get(cache_key)
    if cached_json:
        try:
            parsed_result = Result.model_validate(cached_json)
            l.info("Found cached analysis result")
            return CachedResultResponse(
                message=f"Cached result found for {request.repo_url}:{request.pr_number}:{request_sha}",
                cached=True,
                result=parsed_result
            )
        except Exception as e:
            l.critical(f"Failed to parse cached result: {str(e)}")

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

    parsed_results = Result.model_validate(task_result.get())

    return TaskResultModel(
        task_id=task_id,
        status=task_result.state,
        results=parsed_results,
    )

