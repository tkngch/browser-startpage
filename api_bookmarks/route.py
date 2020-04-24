#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name,unused-variable
# - invalid-name flags `Route`, here we are using CamelCasing method name to
# pretend it is a class. This is mostly personal styling preference.
# - unused-variable flags the methods inside Route, but these methods need to
# defined there, and so, disable unused-variable.
"""api_bookmarks.route."""

from typing import List

from fastapi import APIRouter

from api_bookmarks.service import Service
from api_bookmarks.model import Bookmark
from api_bookmarks.model import BookmarkParameterAdd
from api_bookmarks.model import BookmarkParameterCheck
from api_bookmarks.model import BookmarkParameterDelete
from api_bookmarks.model import BookmarkParameterEdit
from api_bookmarks.model import BookmarkParameterVisit


def Route(service: Service,) -> APIRouter:
    """API route definitions.

    This is a function pretending to be a class, for the consistency with
    Service and Database modules.
    """

    router = APIRouter()

    @router.get("/api/v1/bookmarks", response_model=List[Bookmark])
    async def get_bookmarks():
        """Retrieve all the bookmarks from the database."""
        return service.get_bookmarks()

    @router.post("/api/v1/bookmarks", response_model=List[Bookmark])
    async def add_bookmarks(parameters: List[BookmarkParameterAdd]):
        """Add new bookmarks to the database."""
        return service.add_bookmarks(parameters)

    @router.patch("/api/v1/bookmarks", response_model=List[Bookmark])
    async def update_bookmarks(parameters: List[BookmarkParameterEdit]):
        """Update Bookmarks' attributes."""
        return service.update_bookmarks(parameters)

    @router.put("/api/v1/bookmarks", response_model=List[Bookmark])
    async def check_bookmarks(parameters: List[BookmarkParameterCheck]):
        """Check if a request to the bookmarked site succeeds.

        Depending on the response, Bookmarks' attributes (status, url, title,
        etc) will be updated.
        """
        return service.check_bookmarks(parameters)

    @router.delete("/api/v1/bookmarks")
    async def delete_bookmarks(parameters: List[BookmarkParameterDelete]):
        """Delete the bookmarks from the database.

        Once deleted, a bookmark cannot be un-deleted.
        """
        return service.delete_bookmarks(parameters)

    @router.patch("/api/v1/visit/bookmark", response_model=Bookmark)
    async def visit_bookmark(parameter: BookmarkParameterVisit):
        """Increment the visit count and update the last visit date."""
        return service.visit_bookmark(parameter)

    return router
