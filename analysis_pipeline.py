import json

from logger import AppLogger
from models.output_model import Result
from services.github_services.diff_parser import DiffParser
from services.github_services.get_pr import GitHubService
from services.redis_services.redis_cache import RedisCacheService
from services.ai_services.crew.crew import crew
from typing import Dict, Any, List


class AnalysisPipeline:
    """
    Orchestrates the entire PR analysis process, including caching and AI interaction.
    """
    def __init__(self, github_token: str, task_state_updater=None):
        self.github_service = GitHubService(github_token=github_token)
        self.diff_parser = DiffParser()
        # self.diff_cache = RedisCacheService(db=2)
        self.result_cache = RedisCacheService(db=2)  # <-- Enable result cache
        self.update_state = task_state_updater
        self.logger = AppLogger(name="Pipeline Logger")
        self.logger.info("Initializing analysis pipeline")

    def _update_progress(self, state: str, meta: Dict[str, Any]):
        if self.update_state:
            self.update_state(state=state, meta=meta)

    def _run_crew_analysis(self, parsed_diff: List[Dict[str, Any]]):
        self.logger.info("Starting AI analysis with CrewAI...")
        result_str = crew.kickoff(inputs={"code": parsed_diff}).raw
        self.logger.info("AI crew analysis completed successfully.Results:\n{result}".format(result=result_str))
        return json.loads(result_str)

    def run(self, repo_url: str, pr_number: int) -> dict[str, Any] | Result:
        self._update_progress("INITIALIZING", {"stage": "Fetching PR metadata"})
        self.logger.info("Fetching PR metadata")
        latest_sha = self.github_service.get_pr_head_sha(repo_url, pr_number)
        self.logger.info(f"Latest SHA: {latest_sha}")
        cache_key_result = f"analysis:{repo_url}:{pr_number}:{latest_sha}"

        # --- Step 1: Check cache ---
        cached_result = self.result_cache.get(cache_key_result)
        if cached_result:
            self.logger.info(f"Cache hit for {cache_key_result}. Returning cached result.")
            try:
                return (cached_result)
            except Exception as e:
                self.logger.warning(f"Failed to parse cached result: {str(e)}. Proceeding with fresh analysis.")

        try:
            # --- Step 2: Fresh analysis ---
            patch_text = self.github_service.get_pr_patch(repo_url, pr_number)
            parsed_diff = self.diff_parser.parse(patch_text)

            self._update_progress("ANALYZING_DIFFS", {"stage": "Analyzing PR with AI Crew"})
            self.logger.info("Analyzing PR with AI Crew")
            final_analysis_result = self._run_crew_analysis(parsed_diff)
            self.logger.info(f"Final analysis result:\n{final_analysis_result}")

            # --- Step 3: Store in cache ---
            self.result_cache.set(cache_key_result, final_analysis_result, 86400)
            self.logger.info(f"Result cached under key: {cache_key_result}")

            return (final_analysis_result)

        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise e
