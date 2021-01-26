
from fastapi import FastAPI

from .catalogs import router as catalogs_router
from .cone_search import router as cone_search_router

app = FastAPI()

app.include_router(cone_search_router, prefix="/cone_search")
app.include_router(catalogs_router, prefix="/catalogs")
