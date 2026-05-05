# 🌱 CarbonAI — Sustainability Optimization Platform

AI-driven carbon footprint tracking, scoring, and LLM-powered recommendations.

## Stack
| Layer | Tech |
|-------|------|
| Backend API | FastAPI (Python 3.11) |
| Frontend | Plotly Dash + Bootstrap |
| AI/LLM | OpenAI GPT-4o |
| Database | AWS DynamoDB |
| Deployment | AWS Lambda + Serverless Framework |
| Auth | JWT (bcrypt + PyJWT) |

---

## 🚀 Quick Start (Local Dev)

### 1. Clone & configure
```bash
git clone <repo>
cd carbonai
cp backend/.env.example backend/.env
# Fill in OPENAI_API_KEY and SECRET_KEY in backend/.env
```

### 2. Run with Docker Compose
```bash
cd infrastructure
docker-compose up --build
```
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Frontend Dashboard: http://localhost:8050

### 3. Run without Docker

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

---

## 📁 Project Structure
```
carbonai/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── config.py         # Settings from .env
│   │   ├── models/           # Pydantic data models
│   │   ├── routers/          # API route handlers
│   │   ├── services/         # Business logic + LLM
│   │   └── utils/            # JWT, hashing helpers
│   ├── handler.py            # AWS Lambda entry (Mangum)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app.py            # Dash app + routing
│       ├── pages/            # Dashboard, Emissions, Recommendations, Scoring
│       └── components/       # Charts, Sidebar, Cards
├── infrastructure/
│   ├── docker-compose.yml    # Local dev
│   └── serverless.yml        # AWS Lambda deployment
└── README.md
```

---

## ☁️ Deploy to AWS

### Prerequisites
```bash
npm install -g serverless
pip install serverless-python-requirements
```

### Deploy backend (Lambda + DynamoDB)
```bash
cd backend
export OPENAI_API_KEY=sk-...
export SECRET_KEY=your-production-secret
serverless deploy --stage prod
```

### Deploy frontend
Options:
- **AWS Amplify** — connect GitHub repo, auto-deploy on push
- **EC2** — `docker run -p 8050:8050 carbonai-frontend`
- **Elastic Beanstalk** — upload the frontend Docker container

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login → JWT |
| POST | `/api/emissions/ingest` | Bulk add emission entries |
| GET  | `/api/emissions/summary/{org_id}` | Aggregate summary |
| GET  | `/api/emissions/entries/{org_id}` | List entries |
| GET  | `/api/emissions/trend/{org_id}` | Monthly trend |
| POST | `/api/recommendations/generate` | AI recommendations |
| POST | `/api/scoring/score` | Sustainability score |
| GET  | `/api/scoring/leaderboard` | Org leaderboard |

Full interactive docs at `/docs` (Swagger) or `/redoc`.

---

## 🔧 VS Code Setup

Recommended extensions:
- Python (ms-python.python)
- Pylance
- REST Client (humao.rest-client)
- Docker

Workspace settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```
