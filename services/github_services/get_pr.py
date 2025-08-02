import requests


class GitHubService:
    """
    Handles fetching data from the GitHub API.
    """
    BASE_URL = "https://api.github.com"

    def __init__(self, github_token: str = None):
        """
        Initializes the service with an optional GitHub token.

        Args:
            github_token: A GitHub personal access token for authentication.
        """
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/vnd.github.v3.patch",
            "X-GitHub-Api-Version": "2022-11-28"
        })
        if github_token:
            self._session.headers.update({"Authorization": f"token {github_token}"})
        else:
            print("Warning: No GitHub token provided. Access is limited to public repositories.")

    def get_pr_head_sha(self, repo_url: str, pr_number: int) -> str:
        """
        Fetches only the metadata for a PR to get the head commit SHA.
        """
        print(f"Fetching HEAD SHA for PR #{pr_number}...")
        owner, repo = self._parse_repo_url(repo_url)
        api_url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"

        # We need standard JSON, not a patch, for this call
        headers = {"Accept": "application/vnd.github+json"}
        response = self._session.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()["head"]["sha"]


    def get_pr_patch(self, repo_url: str, pr_number: int) -> str:
        """
        Fetches the raw patch/diff for a specific Pull Request.

        Args:
            repo_url: The full URL of the GitHub repository.
            pr_number: The number of the pull request.

        Returns:
            The raw text of the diff/patch file.

        Raises:
            ValueError: If the repo_url format is invalid.
            requests.exceptions.HTTPError: If the API request fails.
        """
        print(f"Fetching patch for PR #{pr_number} from {repo_url}...")
        try:
            parts = repo_url.strip("/").split("/")
            owner, repo = parts[-2], parts[-1]
        except IndexError:
            raise ValueError("Invalid repo_url format. Expected 'https://github.com/owner/repo'")

        api_url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"

        try:
            response = self._session.get(api_url)
            response.raise_for_status()  # Raises an exception for bad status codes
            print("Successfully fetched patch file.")
            return response.text
        except requests.exceptions.HTTPError as e:
            print(f"Error fetching patch from GitHub: {e}")
            print(f"Response Body: {e.response.text}")
            raise

    def _parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Helper to extract owner/repo from URL."""
        try:
            parts = repo_url.strip("/").split("/")
            return parts[-2], parts[-1]
        except IndexError:
            raise ValueError("Invalid repo_url format.")

