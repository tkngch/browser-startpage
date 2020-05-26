#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""api_bookmarks.database.

This module hosts all the oprations with the database.
"""

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from uuid import UUID
import logging
import sqlite3

from api_bookmarks.model import Bookmark


class Database(ABC):
    """Abstract class for database management."""

    def __init__(self) -> None:
        self._migrate()

    def _migrate(self) -> None:
        """Apply the migration scripts to the database.

        The migration may create and incrementally alter tables.
        """
        migration_scripts = Path(__file__).parent.joinpath("sql").glob("*.sql")
        for script in sorted(migration_scripts):
            self._execute_sql_file(script)

    @abstractmethod
    def _execute_sql_file(self, script: Path) -> None:
        """Execute one sql script."""

    @abstractmethod
    def get_bookmarks(self, bookmark_ids: List[UUID] = None) -> List[Bookmark]:
        """Retrieve bookmarks by their ids from the database.

        If None or an empty list is provided as bookmark ids, all the bookmarks
        are retrieved.
        """

    @abstractmethod
    def add_bookmarks(self, bookmarks: List[Bookmark]) -> None:
        """Insert a new bookmark to the database."""

    @abstractmethod
    def update_bookmarks(self, bookmarks: List[Bookmark], fields: List[str]) -> None:
        """Update Bookmarks' fields.

        Only the listed fields are updated in the database."""

    @abstractmethod
    def delete_bookmarks(self, bookmark_ids: List[UUID]) -> None:
        """Drop the bookmark from the database."""


class SQLite(Database):
    """SQLite database management."""

    def __init__(self, database: str) -> None:
        self.database = database
        super().__init__()

    def _execute_sql_file(self, script: Path) -> None:
        with open(script, "r") as handler:
            content = handler.read()

        logging.info("Executing %s:\n%s", script, content)

        with sqlite3.connect(self.database) as conn:
            conn.executescript(content)
            conn.commit()

    @staticmethod
    def _decode_datetime(value: Optional[datetime]) -> str:
        if value is None:
            return ""
        return value.isoformat()

    @staticmethod
    def _encode_datetime(value: str) -> Optional[datetime]:
        if value == "":
            return None
        return datetime.fromisoformat(value)

    def get_bookmarks(self, bookmark_ids: List[UUID] = None) -> List[Bookmark]:
        tag_denominator = "__;;__"
        with sqlite3.connect(self.database) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            records = self._execute_select_query(cursor, bookmark_ids, tag_denominator)
        conn.close()

        return [
            Bookmark(
                id=record["id"],
                url=record["url"],
                title=record["title"],
                description=record["description"],
                tags=sorted(record["tags"].split(tag_denominator)),
                checkedDatetime=self._encode_datetime(record["checkedDatetime"]),
                lastVisitDatetime=self._encode_datetime(record["lastVisitDatetime"]),
                visitCount=record["visitCount"],
                statusCode=record["statusCode"],
            )
            for record in records
        ]

    @staticmethod
    def _execute_select_query(
        cursor: sqlite3.Cursor,
        bookmark_ids: Optional[List[UUID]],
        tag_denominator: str,
    ) -> List[Any]:
        query = (
            """
            SELECT
                b.id,
                b.url,
                b.title,
                b.description,
                t.tags,
                b.checkedDatetime,
                b.lastVisitDatetime,
                b.visitCount,
                b.statusCode
            FROM bookmark AS b
            LEFT JOIN (
                SELECT bookmarkId, GROUP_CONCAT(name, "%s") AS tags
                FROM tag
                GROUP BY bookmarkId
            ) AS t
            ON b.id = t.bookmarkId
        """
            % tag_denominator
        )
        if bookmark_ids:
            query += "WHERE b.id IN (%s)" % ",".join(["?"] * len(bookmark_ids))
            cursor.execute(query, [str(bid) for bid in bookmark_ids])
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def add_bookmarks(self, bookmarks: List[Bookmark]) -> None:
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                INSERT INTO bookmark (
                    id, url, title, description, checkedDatetime,
                    lastVisitDatetime, visitCount, statusCode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    (
                        str(bookmark.id),
                        bookmark.url,
                        bookmark.title,
                        bookmark.description,
                        self._decode_datetime(bookmark.checkedDatetime),
                        self._decode_datetime(bookmark.lastVisitDatetime),
                        bookmark.visitCount,
                        bookmark.statusCode,
                    )
                    for bookmark in bookmarks
                ],
            )

            tag_insert_args = [
                (tag, str(bookmark.id))
                for bookmark in bookmarks
                for tag in bookmark.tags
            ]
            if tag_insert_args:
                cursor.executemany(
                    "INSERT INTO tag (name, bookmarkId) VALUES (?, ?)", tag_insert_args,
                )
        conn.close()

    def update_bookmarks(self, bookmarks: List[Bookmark], fields: List[str]) -> None:
        bookmark_table_fields = list(set(fields) - set(["tags"]))
        query = (
            "UPDATE bookmark SET "
            + ", ".join(["%s = ?" % field for field in bookmark_table_fields])
            + " WHERE id IS ?"
        )

        parameters = [
            tuple(
                [self._get_field(bookmark, field) for field in bookmark_table_fields]
                + [str(bookmark.id)]
            )
            for bookmark in bookmarks
        ]

        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.executemany(query, parameters)

            if "tags" in fields:
                self._update_tags(cursor, bookmarks)

    def _get_field(self, bookmark: Bookmark, field: str) -> str:
        value = getattr(bookmark, field)
        if "datetime" in field.lower():
            return self._decode_datetime(value)
        return value

    @staticmethod
    def _update_tags(cursor: sqlite3.Cursor, bookmarks: List[Bookmark]) -> None:
        for bookmark in bookmarks:
            cursor.execute(
                "SELECT name FROM tag WHERE bookmarkId IS ?", (str(bookmark.id),),
            )
            old_tags = cursor.fetchall()
            if old_tags and {tag[0] for tag in old_tags} != set(bookmark.tags):
                cursor.execute(
                    "DELETE FROM tag WHERE bookmarkId IS ?", (str(bookmark.id),),
                )

                cursor.executemany(
                    "INSERT INTO tag (name, bookmarkId) VALUES (?, ?)",
                    [(tag, str(bookmark.id)) for tag in bookmark.tags],
                )

    def delete_bookmarks(self, bookmark_ids: List[UUID]) -> None:
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "DELETE FROM bookmark WHERE id = ?",
                [(str(bookmark_id),) for bookmark_id in bookmark_ids],
            )
        conn.close()
