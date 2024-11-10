DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password BINARY NOT NULL,
    active BOOLEAN NOT NULL,
    public_key BINARY
);
