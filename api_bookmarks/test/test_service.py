#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""api_bookmarks.test.test_service."""

from collections import namedtuple
from datetime import datetime
from typing import List
from uuid import UUID

import pytest

from api_bookmarks.database import Database
from api_bookmarks.model import Bookmark
from api_bookmarks.model import BookmarkParameterAdd
from api_bookmarks.model import BookmarkParameterCheck
from api_bookmarks.model import BookmarkParameterDelete
from api_bookmarks.model import BookmarkParameterEdit
from api_bookmarks.model import BookmarkParameterVisit
from api_bookmarks.service import Live


def test_getting() -> None:
    """Test getting bookmarks."""
    database = MockDatabase()
    service = Live(database)
    bookmarks = service.get_bookmarks()
    from_database = database.get_bookmarks()

    assert len(bookmarks) == len(from_database)
    for bm0, bm1 in zip(bookmarks, from_database):
        assert bm0.id == bm1.id
        assert bm0.url == bm1.url
        assert bm0.title == bm1.title
        assert bm0.description == bm1.description
        assert len(bm0.tags) == len(bm1.tags)
        assert set(bm0.tags) == set(bm1.tags)
        assert bm0.checkedDatetime == bm1.checkedDatetime
        assert bm0.lastVisitDatetime == bm1.lastVisitDatetime
        assert bm0.visitCount == bm1.visitCount
        assert bm0.statusCode == bm1.statusCode


def test_adding() -> None:
    """Test adding bookmarks."""
    database = MockDatabase()
    service = Live(database)

    parameters = [
        BookmarkParameterAdd(url="python.org"),
        BookmarkParameterAdd(
            url="https://docs.pytest.org/en/latest/index.html"
        ),
    ]
    bookmarks = service.add_bookmarks(parameters)
    assert len(parameters) == len(bookmarks)

    for parameter, bookmark in zip(parameters, bookmarks):
        assert parameter.url in bookmark.url


def test_updating() -> None:
    """Test updating the bookmarks."""
    database = MockDatabase()
    service = Live(database)

    bookmarks = service.get_bookmarks()

    parameters = [
        BookmarkParameterEdit(
            id=bookmark.id,
            description="Bookmark %.3i" % i,
            tags=["bookmark", "%.3i" % i],
        )
        for i, bookmark in enumerate(bookmarks)
    ]

    updated = service.update_bookmarks(parameters)

    assert len(bookmarks) == len(updated)
    assert len(parameters) == len(updated)

    for i, bookmark in enumerate(bookmarks):
        assert bookmark.id == updated[i].id
        assert parameters[i].id == updated[i].id
        assert bookmark.url == updated[i].url
        assert bookmark.title == updated[i].title
        assert bookmark.lastVisitDatetime == updated[i].lastVisitDatetime
        assert bookmark.visitCount == updated[i].visitCount
        assert bookmark.statusCode == updated[i].statusCode


def test_checking() -> None:
    """Test checking the bookmarks."""
    database = MockDatabase()
    service = Live(database)

    bookmarks = service.get_bookmarks()
    parameters = [
        BookmarkParameterCheck(id=bookmark.id, url=bookmark.url)
        for bookmark in bookmarks
    ]

    updated = service.check_bookmarks(parameters)

    assert len(parameters) == len(updated)
    for parameter, bookmark in zip(parameters, updated):
        assert parameter.id == bookmark.id
        assert parameter.url == bookmark.url


def test_deleting() -> None:
    """Test deleting bookmarks."""
    database = MockDatabase()
    service = Live(database)

    bookmarks = service.get_bookmarks()

    parameters = [
        BookmarkParameterDelete(id=bookmark.id) for bookmark in bookmarks[:1]
    ]
    service.delete_bookmarks(parameters)


def test_visiting() -> None:
    """Test visiting a bookmark."""
    database = MockDatabase()
    service = Live(database)

    bookmarks = service.get_bookmarks()
    parameter = BookmarkParameterVisit(
        id=bookmarks[0].id, visitCount=bookmarks[0].visitCount
    )
    new_bookmark = service.visit_bookmark(parameter)

    assert parameter.id == new_bookmark.id


@pytest.fixture(autouse=True)
def mock_response(monkeypatch):
    """Prevent the actual http request from being sent."""

    MockResponse = namedtuple(
        "MockResponse", ["url", "content", "status_code", "args", "kwargs"]
    )

    def mock_get(url, *args, **kwargs):
        return MockResponse(
            url=url,
            content=b"""
                <!DOCTYPE html>
                <html>
                    <head> <title>Test</title> </head>
                    <body> Hello World </body>
                </html>
            """,
            status_code=401,
            args=args,
            kwargs=kwargs,
        )

    monkeypatch.setattr("api_bookmarks.service.requests.get", mock_get)


class MockDatabase(Database):
    """Mock database module, which does not access the actual database."""

    def _execute_sql_file(self, script: str) -> None:
        return None

    def get_bookmarks(self, bookmark_ids: List[UUID] = None) -> List[Bookmark]:
        datetime_iso_str = "2020-04-11T10:48:07.008968"
        bookmarks = [
            Bookmark(
                id="fa578b6d-50b0-4f68-a6cd-43200cc75e1a",
                url="https://www.python.org/",
                title="Python",
                description="Python programming language",
                tags=["lang", "oss"],
                checkedDatetime=datetime.fromisoformat(datetime_iso_str),
                lastVisitDatetime=datetime.fromisoformat(datetime_iso_str),
                visitCount=10,
                statusCode=200,
            ),
            Bookmark(
                id="3c5d88a6-2550-4910-aca9-d508696ef400",
                url="https://fastapi.tiangolo.com/",
                title="fastapi",
                description="API framework in Python",
                tags=["oss", "backend"],
                checkedDatetime=datetime.fromisoformat(datetime_iso_str),
                lastVisitDatetime=datetime.fromisoformat(datetime_iso_str),
                visitCount=1,
                statusCode=200,
            ),
        ]
        if not bookmark_ids:
            return bookmarks

        return [
            bookmark for bookmark in bookmarks if bookmark.id in bookmark_ids
        ]

    def add_bookmarks(self, bookmarks: List[Bookmark]) -> None:
        return None

    def update_bookmarks(
        self, bookmarks: List[Bookmark], fields: List[str]
    ) -> None:
        return None

    def delete_bookmarks(self, bookmark_ids: List[UUID]) -> None:
        return None
