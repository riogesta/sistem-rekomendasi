CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role INTEGER NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
