import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.database.session import init_db
from backend.app.api.v1 import auth, assignments, rubrics, submissions, evaluations, results, students, dashboard

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("eval_agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database Tables
    logger.info("Initializing Automated Assignment Evaluation Agent database schema...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization warning: {e}")
    yield
    # Shutdown
    logger.info("Shutting down Evaluation Agent backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade Automated Assignment Evaluation Agent platform with RAG, Multi-Agent AI, and Teacher Review.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later or contact support."}
    )

# Mount API Routers
api_v1_router = FastAPI()
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(assignments.router, prefix=f"{settings.API_V1_STR}/assignments", tags=["Assignments"])
app.include_router(rubrics.router, prefix=f"{settings.API_V1_STR}/rubrics", tags=["Rubrics"])
app.include_router(submissions.router, prefix=f"{settings.API_V1_STR}/submissions", tags=["Submissions"])
app.include_router(evaluations.router, prefix=f"{settings.API_V1_STR}/evaluations", tags=["Evaluations & AI Agents"])
app.include_router(results.router, prefix=f"{settings.API_V1_STR}/results", tags=["Published Results"])
app.include_router(students.router, prefix=f"{settings.API_V1_STR}/students", tags=["Students"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard Analytics"])


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER
    }
