"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import analysis_routes, chat_routes, index_routes, source_routes, websocket_routes
from backend.config.settings import settings
from backend.models.api import HealthCheckResponse
from backend.services.analysis.issue_analyzer import create_issue_analyzer
from backend.services.chat.chat_engine import create_chat_engine
from backend.services.chat.session_manager import create_session_manager
from backend.services.indexing.index_manager import create_index_manager
from backend.services.knowledge.kb_manager import create_kb_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Global instances
index_manager = None
session_manager = None
chat_engine = None
kb_manager = None
issue_analyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Initializes services on startup and cleans up on shutdown.
    """
    global index_manager, session_manager, chat_engine, kb_manager, issue_analyzer

    logger.info("Starting application...")

    try:
        # Initialize index manager
        logger.info("Initializing index manager...")
        index_manager = create_index_manager(
            collection_name="documents",
            use_hybrid=True,
            bm25_weight=0.5,
            vector_weight=0.5,
        )

        # Initialize session manager
        logger.info("Initializing session manager...")
        session_manager = create_session_manager()

        # Initialize chat engine
        logger.info("Initializing chat engine...")
        chat_engine = create_chat_engine(
            index_manager=index_manager,
            session_manager=session_manager,
            context_window=settings.chat_context_window,
        )

        # Initialize knowledge base manager
        logger.info("Initializing knowledge base manager...")
        kb_manager = create_kb_manager(base_dir="workspace/knowledge")

        # Initialize issue analyzer (will be set up when Jira is configured)
        # Note: issue_analyzer requires jira_connector which is created on-demand
        # We'll initialize it lazily in analysis_routes when needed
        logger.info("Issue analyzer will be initialized on first use")

        # Initialize route dependencies
        chat_routes.init_chat_routes(chat_engine, session_manager)
        websocket_routes.init_websocket_routes(chat_engine)
        index_routes.init_index_routes(index_manager)
        source_routes.init_source_routes(index_manager)
        analysis_routes.init_analysis_routes(index_manager, kb_manager)

        logger.info("Application started successfully")

        yield

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    finally:
        logger.info("Shutting down application...")
        # Cleanup if needed


# Create FastAPI app
app = FastAPI(
    title="LlamaIndex Chat API",
    description="Chat interface with LlamaIndex + MinerU for multi-source document retrieval",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "detail": str(exc),
        },
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    components = {}

    # Check index manager
    if index_manager:
        try:
            stats = index_manager.get_stats()
            components["index"] = f"ready ({stats.get('total_documents', 0)} docs)"
        except Exception as e:
            components["index"] = f"error: {str(e)}"
    else:
        components["index"] = "not initialized"

    # Check session manager
    if session_manager:
        try:
            sessions = session_manager.list_sessions(limit=1)
            components["sessions"] = f"ready ({len(sessions)} sessions)"
        except Exception as e:
            components["sessions"] = f"error: {str(e)}"
    else:
        components["sessions"] = "not initialized"

    # Check chat engine
    if chat_engine:
        components["chat"] = "ready"
    else:
        components["chat"] = "not initialized"

    return HealthCheckResponse(
        status="healthy" if all(c != "not initialized" for c in components.values()) else "degraded",
        components=components,
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "LlamaIndex Chat API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(chat_routes.router)
app.include_router(websocket_routes.router)
app.include_router(index_routes.router)
app.include_router(source_routes.router)
app.include_router(analysis_routes.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
        log_level="info",
    )
