#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""api_bookmarks.service."""

from abc import ABC
from abc import abstractmethod
from typing import List
from datetime import datetime
from uuid import UUID
from uuid import uuid4
import re

import requests

from api_bookmarks.database import Database
from api_bookmarks.model import Bookmark
from api_bookmarks.model import BookmarkParameterAdd
from api_bookmarks.model import BookmarkParameterCheck
from api_bookmarks.model import BookmarkParameterDelete
from api_bookmarks.model import BookmarkParameterEdit
from api_bookmarks.model import BookmarkParameterVisit
from api_bookmarks.model import DEFAULT_TAGS


class Service(ABC):
    """Business logics."""

    def __init__(self, database: Database) -> None:
        self.database = database

    @abstractmethod
    def get_bookmarks(self, bookmark_ids: List[UUID] = None) -> List[Bookmark]:
        """Retrieve bookmarks from the database."""

    @abstractmethod
    def add_bookmarks(
        self, parameters: List[BookmarkParameterAdd]
    ) -> List[Bookmark]:
        """Add new bookmarks to the database."""

    @abstractmethod
    def update_bookmarks(
        self, parameters: List[BookmarkParameterEdit]
    ) -> List[Bookmark]:
        """Update Bookmarks' attributes."""

    @abstractmethod
    def check_bookmarks(
        self, parameters: List[BookmarkParameterCheck]
    ) -> List[Bookmark]:
        """Check if a GET request to the bookmarked sites succeeds.

        Depending on the response, Bookmarks' attributes (status, url, title,
        favicon) will be updated.
        """

    @abstractmethod
    def delete_bookmarks(
        self, parameters: List[BookmarkParameterDelete]
    ) -> None:
        """Delete the bookmarks from the database.

        Once deleted, a bookmark cannot be un-deleted.
        """

    @abstractmethod
    def visit_bookmark(self, parameter: BookmarkParameterVisit) -> Bookmark:
        """Increment the visit count and update the last visit date."""


class Live(Service):
    """Service implementation."""

    def get_bookmarks(self, bookmark_ids: List[UUID] = None) -> List[Bookmark]:
        return self.database.get_bookmarks(bookmark_ids)

    def add_bookmarks(
        self, parameters: List[BookmarkParameterAdd]
    ) -> List[Bookmark]:

        bookmarks = []
        for parameter in parameters:
            bookmark = self._construct_bookmark(parameter.url)
            bookmark.tags = DEFAULT_TAGS
            bookmarks.append(bookmark)

        self.database.add_bookmarks(bookmarks)
        return bookmarks

    def update_bookmarks(
        self, parameters: List[BookmarkParameterEdit]
    ) -> List[Bookmark]:

        updates = [
            Bookmark(
                id=parameter.id,
                description=parameter.description,
                tags=parameter.tags if parameter.tags else DEFAULT_TAGS,
            )
            for parameter in parameters
        ]
        self.database.update_bookmarks(updates, ["description", "tags"])
        return self.get_bookmarks([parameter.id for parameter in parameters])

    def check_bookmarks(
        self, parameters: List[BookmarkParameterCheck]
    ) -> List[Bookmark]:
        bookmarks = []
        for parameter in parameters:
            bookmark = self._construct_bookmark(parameter.url)
            bookmark.id = parameter.id
            bookmarks.append(bookmark)

        self.database.update_bookmarks(
            bookmarks, ["url", "title", "statusCode", "checkedDatetime"],
        )
        return self.get_bookmarks([parameter.id for parameter in parameters])

    def delete_bookmarks(
        self, parameters: List[BookmarkParameterDelete]
    ) -> None:
        self.database.delete_bookmarks(
            [parameter.id for parameter in parameters]
        )

    def visit_bookmark(self, parameter: BookmarkParameterVisit) -> Bookmark:
        new_parameter = BookmarkParameterVisit(
            id=parameter.id,
            visitCount=parameter.visitCount + 1,
            lastVisitDatetime=self._get_datetime(),
        )
        self.database.update_bookmarks(
            [new_parameter], ["visitCount", "lastVisitDatetime"]
        )
        return self.get_bookmarks([parameter.id])[0]

    @staticmethod
    def _get_datetime() -> datetime:
        return datetime.now()

    def _construct_bookmark(self, url: str) -> Bookmark:
        """Retrieve the URL of the resource.

        If URL does not start with "http", http protocol is assumed, as opposed
        to https.

        This method follows a redirect, if any, and retrieves the redirected
        destination URL.
        """
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        # Python's urllib.request.urlopen fails at Status 308 (permanent
        # redirect), so here, use requests library instead.
        response = requests.get(url)

        content = response.content.decode("utf-8", errors="ignore")
        title = re.split(
            "</title>",
            re.split("<title>", content, flags=re.IGNORECASE)[1],
            flags=re.IGNORECASE,
        )[0]

        bookmark = Bookmark(
            id=uuid4(),
            url=response.url,
            title=title,
            statusCode=response.status_code,
            checkedDatetime=self._get_datetime(),
        )
        return bookmark
