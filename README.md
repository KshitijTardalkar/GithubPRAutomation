# GitHub PR Automation

Welcome to the **GitHub PR Automation** repository!  
This project automates the analysis of GitHub Pull Requests (PRs) using a modular service-oriented architecture powered by Celery, Redis, and AI-backed insights.

---

## 🚀 Features

### 🔍 PR Analysis Pipeline
- Core logic resides in `app/analysis_pipeline.py`.
- Contains the `AnalysisPipeline` class with a `run()` method to initiate PR analysis.

### ⚙️ Celery Integration
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

## 🛠️ Installation

Clone the repository:

```bash
git clone https://github.com/KshitijTardalkar/GithubPRAutomation.git
cd GithubPRAutomation
```

---

## ⚙️ Usage

### 1. Configuration Environment

#### Setting Up API Keys

1. **Obtain GitHub API Key:**
   - Go to [GitHub Developer Settings](https://github.com/settings/tokens).
   - Click on "Generate new token". Select the scopes you need, typically including `repo` for accessing 
repositories.
   - Generate and copy the token.

2. **Obtain Gemini API Key:**
   - Visit the Gemini platform's website or API service.
   - Follow their documentation to generate an API key.
   - Store the key securely.

#### Configure Environment Variables

1. **Create a `.env` File:**
   - Copy `example.env` to create a new file named `.env` in the root directory of your project.
   ```bash
   cp .env.example .env
   ```

2. **Add API Keys to `.env`:**
   - Open the `.env` file and add your API keys:
     ```
     GITHUB_API_KEY=<Your-Github-API-Key>
     GEMINI_API_KEY=<Your-Gemini-API-Key>
     ```

#### Environment Setup

1. **Install Required Libraries:**
   - Ensure you have the necessary libraries installed by running:
     ```bash
     pip install -r requirements.txt
     ```

2. **Ensure Services are Running:**
   - Make sure Redis and Celery services are set up and running as specified in the Usage section.

#### Security Best Practices

1. **Protect `.env` File:**
   - Do not push the `.env` file to your public repository.
   - Ensure it is listed in your `.gitignore`.

2. **Regular Key Rotation:**
   - Rotate API keys periodically and review access permissions.


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
- If the PR has been recently analyzed and is present in the Redis cache, it will return the cached result immediately.
- If the PR is not cached or has changed since the last analysis, a new Celery task will be created. The response will include a task_id that can be used to check the status or retrieve results using the GET endpoints described below.
```bash
curl -X POST http://127.0.0.1:8000/analyze_pr \
  -H "Content-Type: application/json" \
  -d '{
        "repo_url": <YOUR_GITHUB_URL>,
        "pr_number": <PR_NUMBER>,
        "github_token": <OPTIONAL_GITHUB_TOKEN>
      }'
```

**Note**: Access to public repositories without a GitHub token is subject to strict rate limits. To access private repositories and increase your rate limit, provide a valid GitHub API token.

#### 2. Check Task Status (using Celery task ID)
```bash
curl http://127.0.0.1:8000/status/<task_id>
```

#### 3. Check Task Result (using Celery task ID)
```bash
curl http://127.0.0.1:8000/result/<task_id>
```