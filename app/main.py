
from fastapi import FastAPI

from .catalogs import router as catalogs_router
from .cone_search import router as cone_search_router

tags_metadata = [
    {
        "name": "catalogs",
        "description": "Listing of available catalogs",
    },
    {
        "name": "cone_search",
        "description": "Search for objects in a cone around a celestial direction",
    },
]

app = FastAPI(
    title="Ampel Catalog Matching Service",
    description="Match celestial coordinates against catsHTM and extcats catalogs",
    version="0.1",
    openapi_tags=tags_metadata,
)

app.include_router(cone_search_router, prefix="/cone_search", tags=["cone_search"])
app.include_router(catalogs_router, prefix="/catalogs", tags=["catalogs"])

