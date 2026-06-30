from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fairproxy_api.cache import setup_cache
from fairproxy_api.routers import get_router

# Initialize cache configuration
setup_cache()

app = FastAPI(
    title="FAIRification API",
    description="A FAIRification proxy API over heterogeneous datastores (Socrata, MTNA RDS, US Census).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(get_router())


@app.get("/status")
async def status() -> dict[str, str]:
    """Health status API."""
    return {"status": "pass", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("fairproxy_api.main:app", host="0.0.0.0", port=8000, reload=True)
