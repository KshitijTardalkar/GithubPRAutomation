import json

from models.output_model import Result
from services.github_services.diff_parser import DiffParser
from services.github_services.get_pr import GitHubService
from services.redis_services.redis_cache import RedisCacheService
from services.ai_services.crew.crew import crew
from typing import Dict, Any, List


# # Mocking crew for standalone execution
# class MockCrew:
#     def kickoff(self, inputs):
#         class MockResult:
#             raw = json.dumps({
#                 "files": [
#                     {
#                         "name": "app/modules/auth/auth_service.py",
#                         "issues": [
#                             {
#                                 "type": "Best Practice",
#                                 "line": 26,
#                                 "description": "The token expiration time '1200s' is a hardcoded 'magic string'.",
#                                 "suggestion": "Consider moving this value to a configuration file or an environment variable."
#                             }
#                         ]
#                     }
#                 ],
#                 "summary": {
#                     "total_files": 1,
#                     "total_issues": 1,
#                     "critical_issues": 0
#                 }
#             })
#
#         return MockResult()
#
#
# crew = MockCrew()


class AnalysisPipeline:
    """
    Orchestrates the entire PR analysis process, including caching and AI interaction.
    """

    def __init__(self, github_token: str, task_state_updater=None):
        self.github_service = GitHubService(github_token=github_token)
        self.diff_parser = DiffParser()
        self.diff_cache = RedisCacheService(db=2)
        # self.result_cache = RedisCacheService(db=3)
        self.update_state = task_state_updater

    def _update_progress(self, state: str, meta: Dict[str, Any]):
        """Safely updates task state if a handler is provided."""
        if self.update_state:
            self.update_state(state=state, meta=meta)

    def _run_crew_analysis(self, parsed_diff: List[Dict[str, Any]]):
        """Encapsulates the call to the AI crew."""
        print("Starting AI analysis with CrewAI...")
        result_str = crew.kickoff(inputs={"code": parsed_diff}).raw
        # This function is now responsible for parsing the raw string from the crew
        return json.loads(result_str)

    def run(self, repo_url: str, pr_number: int) -> Dict[str, Any]:
        """
        Executes the full analysis pipeline.
        """
        self._update_progress("INITIALIZING", {"stage": "Fetching PR metadata"})
        latest_sha = self.github_service.get_pr_head_sha(repo_url, pr_number)

        cache_key_result = f"pr_analysis_result:{repo_url}:{pr_number}:{latest_sha}"

        try:
            patch_text = self.github_service.get_pr_patch(repo_url, pr_number)
            parsed_diff = self.diff_parser.parse(patch_text)

            self._update_progress("ANALYZING_DIFFS", {"stage": "Analyzing PR with AI Crew"})

            final_analysis_result = self._run_crew_analysis(parsed_diff)
            print("Final analysis result:", final_analysis_result)

            return final_analysis_result
        except Exception as e:
            # Propagate the exception to be handled by the Celery task
            raise e