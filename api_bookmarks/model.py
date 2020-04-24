#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods
"""api_bookmarks.model."""

from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel  # pylint: disable=no-name-in-module


DEFAULT_TAGS = ["*unassigned"]


class Bookmark(BaseModel):
    """Bookmark entry.

    Note that the frontend expects camelCased field names, not snake_cased. So
    the fields in this class are all camelCased.
    """

    id: Optional[UUID] = None
    url: str = ""
    title: str = ""
    description: str = ""
    tags: List[str] = DEFAULT_TAGS
    checkedDatetime: Optional[datetime] = None
    lastVisitDatetime: Optional[datetime] = None
    visitCount: int = 0
    statusCode: int = 0


class BookmarkParameterAdd(BaseModel):
    """Parameter to add a new bookmark."""

    url: str


class BookmarkParameterEdit(BaseModel):
    """Parameter to edit a bookmark."""

    id: UUID
    description: str
    tags: List[str]


class BookmarkParameterCheck(BaseModel):
    """Parameter to check and update a bookmark."""

    id: UUID
    url: str


class BookmarkParameterDelete(BaseModel):
    """Parameter to delete a bookmark."""

    id: UUID


class BookmarkParameterVisit(BaseModel):
    """Parameter to visit a bookmark."""

    id: UUID
    visitCount: int
    lastVisitDatetime: Optional[datetime] = None
