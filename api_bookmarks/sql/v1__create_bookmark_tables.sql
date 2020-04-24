PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS bookmark (
    id TEXT PRIMARY KEY,
    url TEXT UNIQUE,
    title TEXT,
    description TEXT,
    checkedDatetime TEXT,
    lastVisitDatetime TEXT,
    visitCount INT DEFAULT 0,
    statusCode INT
);

CREATE TABLE IF NOT EXISTS tag (
    name TEXT NOT NULL,
    bookmarkId TEXT NOT NULL,
    FOREIGN KEY (bookmarkId) REFERENCES bookmark(id) ON DELETE CASCADE
);
