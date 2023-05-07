-- CREATE TABLE users(
-- id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
-- username TEXT NOT NULL, 
-- password NOT NULL);

-- CREATE TABLE library(
-- book_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
-- book_name TEXT NOT NULL, 
-- authors TEXT NOT NULL, 
-- book_cover TEXT NOT NULL, 
-- published_date TEXT NOT NULL,
-- book_description TEXT,
-- book_genre TEXT NOT NULL,
-- book_publisher TEXT,
-- book_pages TEXT,
-- date_added TEXT DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')), 
-- user_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id));

-- CREATE TABLE temp_library(
-- temp_id INTEGER, 
-- book_name TEXT NOT NULL, 
-- authors TEXT NOT NULL, 
-- book_cover TEXT NOT NULL, 
-- published_date TEXT NOT NULL,
-- book_description TEXT,
-- book_genre TEXT NOT NULL,
-- book_publisher TEXT,
-- book_pages TEXT,
-- user_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id));

-- CREATE TABLE history (
-- position_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
-- book_name TEXT NOT NULL, 
-- author TEXT NOT NULL, 
-- date_added TEXT DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')), 
-- user_id INTEGER NOT NULL, 
-- FOREIGN KEY(user_id) REFERENCES users(id));

-- Acc for testing
-- ADMIN1, admin111


-- DROP TABLE temp_library;
-- DROP TABLE users;
-- DROP TABLE library;
-- DROP TABLE history;


SELECT * FROM temp_library;
SELECT * FROM users;
SELECT * FROM library;
SELECT * FROM history;