#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""api_bookmarks.test.test_database."""

from typing import List
from datetime import datetime
from pathlib import Path
from itertools import product

from api_bookmarks.database import Database
from api_bookmarks.database import SQLite
from api_bookmarks.model import Bookmark


def test_adding(tmp_path: Path) -> None:
    """Test adding bookmarks to the database."""
    filepath = tmp_path.joinpath("bookman.sqlite3").as_posix()
    database = SQLite(filepath)

    bookmarks = _make_bookmarks()
    database.add_bookmarks(bookmarks)

    _compare_bookmarks_against_database(database, bookmarks)


def test_updaging(tmp_path: Path) -> None:
    """Test updating bookmarks in the database."""
    filepath = tmp_path.joinpath("bookman.sqlite3").as_posix()
    database = SQLite(filepath)

    bookmarks = _make_bookmarks()
    database.add_bookmarks(bookmarks)

    new_bookmarks = bookmarks[:]
    new_bookmarks[0].lastVisitDatetime = datetime.now()
    new_bookmarks[0].visitCount += 1
    new_bookmarks[1].tags = ["new tag0", "new tag1"]
    database.update_bookmarks(
        new_bookmarks, ["lastVisitDatetime", "visitCount", "tags"]
    )

    _compare_bookmarks_against_database(database, new_bookmarks)


def test_deleting(tmp_path: Path) -> None:
    """Test deleting bookmarks from the database."""
    filepath = tmp_path.joinpath("bookman.sqlite3").as_posix()
    database = SQLite(filepath)

    bookmarks = _make_bookmarks()
    database.add_bookmarks(bookmarks)

    database.delete_bookmarks([bookmarks[0].id])
    new_bookmarks = bookmarks[1:]

    _compare_bookmarks_against_database(database, new_bookmarks)
    assert not database.get_bookmarks([bookmarks[0].id])


def _compare_bookmarks_against_database(
    database: Database, bookmarks: List[Bookmark]
) -> None:
    """Compare the bookmarks against the database records.

    Any mismatch (e.g., extra records in bookmarks that are not in the
    database) results in assertion error.
    """
    retrieved_bookmarks = database.get_bookmarks()
    assert len(bookmarks) == len(retrieved_bookmarks)

    n_matches = 0
    for bm0, bm1 in product(bookmarks, retrieved_bookmarks):
        if bm0.id != bm1.id:
            continue

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
        n_matches += 1

    assert n_matches == len(bookmarks)


def _make_bookmarks() -> List[Bookmark]:
    return [
        Bookmark(
            id="fa578b6d-50b0-4f68-a6cd-43200cc75e1a",
            url="https://www.python.org/",
            title="Python",
            description="Python programming language",
            tags=["lang", "oss"],
            checkedDatetime=datetime.now(),
            lastVisitDatetime=datetime.now(),
            visitCount=10,
            statusCode=200,
        ),
        Bookmark(
            id="3c5d88a6-2550-4910-aca9-d508696ef400",
            url="https://fastapi.tiangolo.com/",
            title="fastapi",
            description="API framework in Python",
            tags=["oss", "backend"],
            checkedDatetime=datetime.now(),
            lastVisitDatetime=datetime.now(),
            visitCount=1,
            statusCode=200,
        ),
    ]
