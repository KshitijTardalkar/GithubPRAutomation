# GitHub PR Automation

Welcome to the **GitHub PR Automation** repository!  
This project automates the analysis of GitHub Pull Requests (PRs) using a modular service-oriented 
architecture powered by Celery, Redis, and AI-backed insights.

---

## 🚀 Features

### 🔍 PR Analysis Pipeline
- Core logic resides in `app/analysis_pipeline.py`.
- Contains the `AnalysisPipeline` class with a `run()` method to initiate PR analysis.

### ⚙ Celery Integration
- Asynchronous task processing using Celery.
- Task defined as `analyze_pr_task` in `app/celery_app.py`.

### 🧱 Service-Oriented Architecture
Modular services in the `services/` directory:
- **AI Services**: `services/ai_services`
- **GitHub Services**: `services/github_services`
- **Logging Services**: `services/logging_services`
- **Redis Caching Services**: `services/redis_services`

### 📦 Model Definitions
- API request/response models: `models/api_models.py`
- Output data structures: `models/output_model.py`

### 📝 Logging
- Centralized logging with `AppLogger` in `services/logging_services/logger.py`.

### 🧠 Redis Caching
- `RedisCacheService` handles Redis operations in `services/redis_services/redis_cache.py`.

---

## 🛠 Installation

Clone the repository:

```bash
git clone https://github.com/KshitijTardalkar/GithubPRAutomation.git
cd GithubPRAutomation
```

---


## ⚙ Usage

### 1. Configuration Environment

#### Setting Up API Keys

1. **Obtain GitHub API Key:**
   - Go to [GitHub Developer Settings](https://github.com/settings/tokens).
   - Click on "Generate new token". Select the scopes you need, typically including `repo` for accessing 
repositories.
   - Generate and copy the token.
   - Pass this token in the POST request to authenticate API calls. This enables higher rate limits and 
access to private repositories.
2. **Obtain Gemini API Key:**
   - Visit the Gemini platform's website or API service.
   - Follow their documentation to generate an API key.
   - Store the key securely.

#### Configure API Keys

   - Set Environment Variables:

        Export your Gemini API key directly in your terminal (no `.env` file is used):

      ```bash
      export GEMINI_API_KEY=<your-gemini-api-key>
     ```

   - GitHub Token Usage:

   You do not need to set the GitHub token as an environment variable.
   Instead, pass the token directly in the POST request payload when making authenticated GitHub API 
calls.
   This allows access to private repositories and increases your rate limit.

#### Environment Setup

1. **Install Required Libraries:**
   - Ensure you have the necessary libraries installed by running:
     ```bash
     pip install -r requirements.txt
     ```

2. **Ensure Services are Running:**
   - Make sure Redis and Celery services are set up and running as specified in the next section.



### 2. Start services
- Run Redis(via Docker):
```bash
docker run -p 6379:6379 -d redis
```

- Start Celery Worker:
```bash
celery -A app.celery_app worker --loglevel=info
```

### 3. Run the Application
```bash
uvicorn app.main:app --reload
```

## 📡 API Usage

Use the FastAPI endpoints defined in `app/main.py` to interact with the system programmatically.  
You can test them using tools like **Postman** or **cURL**.

### 🔁 Sample cURL Requests

#### 1. Analyze a PR: 
This command will do one of two things:
- If the PR has been recently analyzed and is present in the Redis cache, it will return the cached 
result immediately.
- If the PR is not cached or has changed since the last analysis, a new Celery task will be created. The 
response will include a task_id that can be used to check the status or retrieve results using the GET 
endpoints described below.

```bash
curl -X POST http://127.0.0.1:8000/analyze_pr \
  -H "Content-Type: application/json" \
  -d '{
        "repo_url": <YOUR_GITHUB_URL>,
        "pr_number": <PR_NUMBER>,
        "github_token": <OPTIONAL_GITHUB_TOKEN>
      }'
```

**Note**: Access to public repositories without a GitHub token is subject to strict rate limits. To 
access private repositories and increase your rate limit, provide a valid GitHub API token.

#### 2. Check Task Status (using Celery task ID)
```bash
curl http://127.0.0.1:8000/status/<task_id>
```

#### 3. Check Task Result (using Celery task ID)
```bash
curl http://127.0.0.1:8000/result/<task_id>
```

### 🧪 API Testing using `test.http`

You can also test the API using `test.http`.  
It works with both JetBrains IDEs and VSCode (with the REST Client extension).

- Fill in the required placeholders manually, or
- Optionally create a `test.http.env.json` to manage local test values.

---

# Contributing

Contributions are welcome! Please follow these guidelines when contributing:

1. **Report Issues**: If you encounter any issues or have feature requests, please open an issue on the 
GitHub repository.
2. **Submit Pull Requests**: Fork the repository and submit a pull request with your changes. Ensure 
that the code is well-documented and follows the project's coding standards.

## License

This project is licensed under the [MIT License](LICENSE).  
Feel free to modify and distribute this software as needed for your use cases.

---

# Contact Us

If you have any questions or need further assistance with the GitHub PR Automation project, feel free to 
reach out:

- **Email**: kstardalkar@gmail.com
- **GitHub**: [@KshitijTardalkar](https://github.com/KshitijTardalkar)

Thank you for using the GitHub PR Automation repository!

