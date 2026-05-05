from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import emissions, recommendations, scoring, auth
from app.config import settings

app = FastAPI(
    title="CarbonAI API",
    description="Sustainability Optimization Platform — AI-driven carbon reduction insights",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(emissions.router, prefix="/api/emissions", tags=["emissions"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(scoring.router, prefix="/api/scoring", tags=["scoring"])


@app.get("/")
def root():
    return {"message": "CarbonAI API is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
