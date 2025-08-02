import os
from celery import Celery
from analysis_pipeline import AnalysisPipeline

# --- Celery App Configuration ---
# DB 0: Message Broker
# DB 1: Celery's own result backend (tracks task state and return values)
celery_app = Celery(
    "celery_app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)
celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

# --- Celery Task Definition ---
@celery_app.task(bind=True, name="celery_app.analyze_pr")
def analyze_pr_task(self, repo_url: str, pr_number: int):
    """
    A thin wrapper that executes the main analysis pipeline.
    The complex logic is now encapsulated in the AnalysisPipeline class.
    """
    try:
        # --- Initialization within the worker ---
        github_token = os.environ.get("GITHUB_API_TOKEN")
        if not github_token:
            print("GITHUB_API_TOKEN environment variable not set. Can only analyse public repositories.")

        # Instantiate the main pipeline orchestrator.
        # We pass the task's `self.update_state` method so the pipeline
        # can report its progress back to Celery.
        pipeline = AnalysisPipeline(
            github_token=github_token,
            task_state_updater=self.update_state
        )

        # Execute the pipeline and return its result.
        # The return value is automatically stored in Celery's backend (DB 1).
        res = pipeline.run(repo_url, pr_number)
        return res

    except Exception as e:
        # Let Celery handle the failure state
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise