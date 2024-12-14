from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.api import contacts, auth, users

# Initialize the FastAPI application
app = FastAPI()

# CORS (Cross-Origin Resource Sharing) configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles exceptions raised when the request rate limit is exceeded.

    Args:
        request (Request): The incoming HTTP request that triggered the exception.
        exc (RateLimitExceeded): The exception instance for rate limit exceeded.

    Returns:
        JSONResponse: A response with status code 429 and an error message.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )


# Include routers for different API endpoints
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    # Run the application using Uvicorn server
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
