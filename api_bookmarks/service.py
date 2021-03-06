#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""api_bookmarks.service."""

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from html import unescape
from typing import List
from unicodedata import normalize
from urllib.parse import urlparse
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
    def add_bookmarks(self, parameters: List[BookmarkParameterAdd]) -> List[Bookmark]:
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
    def delete_bookmarks(self, parameters: List[BookmarkParameterDelete]) -> None:
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

    def add_bookmarks(self, parameters: List[BookmarkParameterAdd]) -> List[Bookmark]:

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

    def delete_bookmarks(self, parameters: List[BookmarkParameterDelete]) -> None:
        self.database.delete_bookmarks([parameter.id for parameter in parameters])

    def visit_bookmark(self, parameter: BookmarkParameterVisit) -> Bookmark:
        new_parameter = Bookmark(
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
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        content = response.content.decode("utf-8", errors="ignore")

        # If the page does not have a title tag (e.g., direct link to a file),
        # the last part of url is assumed title.
        title = self._extract_title(content, response.url)
        bookmark = Bookmark(
            id=uuid4(),
            url=response.url,
            title=title,
            statusCode=response.status_code,
            checkedDatetime=self._get_datetime(),
        )
        return bookmark

    @staticmethod
    def _extract_title(content: str, url: str) -> str:
        default_title = urlparse(url).path.strip("/").split("/")[-1]

        # A website can have a title tag inside the body, in which case
        # `re.search` returns the last title tag in the body. So limit
        # search to inside the head.
        head = re.search(
            "<head(.*)>(.*)</head>", content, flags=re.IGNORECASE | re.DOTALL
        )

        if head is None:
            return default_title

        title_match = re.search(
            "<title(.*)>(.*)</title>", head.group(0), flags=re.IGNORECASE | re.DOTALL,
        )
        if title_match is None:
            return default_title

        # Unescape the HTML escape sequence: for example, convert "&amp;"
        # to "&".
        # And normalize to unicode string: for example, "\xa0" to " " (white
        # space).
        return normalize("NFKD", unescape(title_match.group(2)).strip())
