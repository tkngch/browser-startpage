#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""API for startpage."""

from os import getenv
from os.path import expandvars
from pathlib import Path

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from api_bookmarks import SQLite
from api_bookmarks import Live
from api_bookmarks import Route


DIST = Path(__file__).parent.joinpath("dist")

app = FastAPI()
app.mount(
    "/fonts", StaticFiles(directory=DIST.joinpath("fonts")), name="fonts"
)
app.mount("/js", StaticFiles(directory=DIST.joinpath("js")), name="js")
app.mount("/css", StaticFiles(directory=DIST.joinpath("css")), name="css")


@app.get("/")
async def root():
    """Serve a single HTML file."""
    return FileResponse(path=DIST.joinpath("index.html"))


@app.get("/{resource}", include_in_schema=False)
def serve_static(resource: str):
    """Serve a static file, if it exists."""
    resource_path = DIST.joinpath(resource)
    if resource_path.is_file():
        return FileResponse(path=resource_path)

    return FileResponse(path=DIST.joinpath("index.html"))


def _define_bookmark_api_route() -> APIRouter:
    """Define the API routes."""
    database = SQLite(_get_data_dir().joinpath("bookmarks.sqlite3").as_posix())
    service = Live(database)
    return Route(service)


def _get_data_dir() -> Path:
    xdg_data = Path(expandvars("$HOME")).joinpath(".local").joinpath("share")
    env_xdg_data = getenv("XDG_DATA_HOME", None)
    if env_xdg_data:
        xdg_data = Path(xdg_data)

    data_dir = xdg_data.joinpath("startpage")
    data_dir.mkdir(exist_ok=True)
    return data_dir


app.include_router(_define_bookmark_api_route())

# Allow CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    # Note that the port number has to be the same as the one hard-coded in
    # src/services/BookmarkService.js.
    uvicorn.run(
        "main:app", host="127.0.0.1", port=33875, log_level="info", reload=True
    )
