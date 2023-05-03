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

-- CREATE TABLE history (
--   position_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
--   book_name TEXT NOT NULL, 
--   author TEXT NOT NULL, 
--   date_added TEXT DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')), 
--   user_id INTEGER NOT NULL, 
--   FOREIGN KEY(user_id) REFERENCES users(id)
-- );

-- INSERT INTO users(username, password)
-- VALUES ("ADMIN", "admin123");

-- INSERT INTO library(book_name, author, book_cover, user_id) VALUES ("Test book", "Me", "https://johannatarkela.com/wp-content/uploads/2020/05/BookCover1.jpg", 1);
-- DROP TABLE library;

-- DELETE FROM users WHERE id=1;
-- UPDATE users SET id=1 WHERE id=2;

-- DROP TABLE library;
-- DROP TABLE history;

-- username: ADMIN1 password: admin1

-- DELETE FROM library WHERE book_id < 20;


SELECT * FROM users;
SELECT * FROM library;
SELECT * FROM history;