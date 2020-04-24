#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""api_bookmarks.test.test_route."""

from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api_bookmarks.model import Bookmark
from api_bookmarks.model import BookmarkParameterAdd
from api_bookmarks.model import BookmarkParameterCheck
from api_bookmarks.model import BookmarkParameterDelete
from api_bookmarks.model import BookmarkParameterEdit
from api_bookmarks.model import BookmarkParameterVisit
from api_bookmarks.service import Service
from api_bookmarks.route import Route


def test_getting() -> None:
    """Test getting bookmarks through the get api."""
    service = MockService()
    route = Route(service)

    app = FastAPI()
    app.include_router(route)

    client = TestClient(app)

    response = client.get("/api/v1/bookmarks")
    _check_response(response, service)


def test_adding() -> None:
    """Test adding bookmarks through the post api."""
    service = MockService()
    route = Route(service)

    app = FastAPI()
    app.include_router(route)

    client = TestClient(app)

    response = client.post(
        "/api/v1/bookmarks", json=[{"url": "archlinux.org"}],
    )
    _check_response(response, service)


def test_updating() -> None:
    """Test updating bookmarks through the patch api."""
    service = MockService()
    route = Route(service)

    app = FastAPI()
    app.include_router(route)

    client = TestClient(app)

    response = client.patch(
        "/api/v1/bookmarks",
        json=[
            {
                "id": str(bookmark.id),
                "description": "Bookmark %s" % bookmark.title,
                "tags": bookmark.tags,
            }
            for bookmark in service.bookmarks
        ],
    )
    _check_response(response, service)


def test_checking() -> None:
    """Test chekcing bookmarks through the put api."""
    service = MockService()
    route = Route(service)

    app = FastAPI()
    app.include_router(route)

    client = TestClient(app)

    response = client.put(
        "/api/v1/bookmarks",
        json=[
            {"id": str(bookmark.id), "url": bookmark.url,}
            for bookmark in service.bookmarks
        ],
    )
    _check_response(response, service)


def test_deleting() -> None:
    """Test deleting bookmarks through the delete api."""
    service = MockService()
    route = Route(service)

    app = FastAPI()
    app.include_router(route)

    client = TestClient(app)

    response = client.delete(
        "/api/v1/bookmarks",
        json=[{"id": str(bookmark.id)} for bookmark in service.bookmarks],
    )
    assert response.status_code == 200
    assert response.json() is None


def test_visiting() -> None:
    """Test visiting a bookmark through the patch api."""
    service = MockService()
    route = Route(service)

    app = FastAPI()
    app.include_router(route)

    client = TestClient(app)
    original = service.bookmarks[0]
    response = client.patch(
        "/api/v1/visit/bookmark",
        json={
            "id": str(original.id),
            "visitCount": original.visitCount,
            "lastVisitDatetime": original.lastVisitDatetime.isoformat(),
        },
    )
    assert response.status_code == 200

    returned = Bookmark(**response.json())
    assert original.id == returned.id
    assert original.lastVisitDatetime < returned.lastVisitDatetime
    assert original.visitCount + 1 == returned.visitCount


def _check_response(response, service):
    assert response.status_code == 200

    returned_bookmarks = response.json()
    assert len(returned_bookmarks) == len(service.bookmarks)

    for res, original in zip(returned_bookmarks, service.bookmarks):
        returned = Bookmark(**res)
        assert original.id == returned.id
        assert original.url == returned.url
        assert original.title == returned.title
        assert original.description == returned.description
        assert len(original.tags) == len(returned.tags)
        assert set(original.tags) == set(returned.tags)
        assert original.checkedDatetime == returned.checkedDatetime
        assert original.lastVisitDatetime == returned.lastVisitDatetime
        assert original.visitCount == returned.visitCount
        assert original.statusCode == returned.statusCode


class MockService(Service):
    """Mock service module."""

    def __init__(self) -> None:
        super().__init__(None)

    def get_bookmarks(self, bookmark_ids: List[UUID] = None) -> List[Bookmark]:
        if not bookmark_ids:
            return self.bookmarks
        return [
            bookmark
            for bookmark in self.bookmarks
            if bookmark.id in bookmark_ids
        ]

    def add_bookmarks(
        self, parameters: List[BookmarkParameterAdd]
    ) -> List[Bookmark]:
        return self.bookmarks

    def update_bookmarks(
        self, parameters: List[BookmarkParameterEdit]
    ) -> List[Bookmark]:
        return self.bookmarks

    def check_bookmarks(
        self, parameters: List[BookmarkParameterCheck]
    ) -> List[Bookmark]:
        return self.bookmarks

    def delete_bookmarks(
        self, parameters: List[BookmarkParameterDelete]
    ) -> None:
        return None

    def visit_bookmark(self, parameter: BookmarkParameterVisit) -> Bookmark:
        bookmark = self.get_bookmarks([parameter.id])[0]
        bookmark.visitCount += 1
        bookmark.lastVisitDatetime = datetime.fromisoformat(
            "2020-04-11T13:48:07.008968"
        )
        return bookmark

    @property
    def bookmarks(self) -> List[Bookmark]:
        """Get the bookmarks for testing."""
        datetime_iso_str = "2020-04-11T10:48:07.008968"
        return [
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
