import os
import sqlite3
import random

from functions import login_required, search_books
from flask import Flask, flash, get_flashed_messages, url_for, render_template, redirect, session, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Connect to the static folder containing css and js files
app = Flask(__name__, static_url_path='/static')

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Secret key to use flash messages
app.secret_key='admin12345'

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


# Main page
@app.route('/')
def index():
    return render_template('index.html')


# About ReadRoll
@app.route('/about')
def about():
    return render_template('about.html')


# Display a selected book from user's library
@app.route('/book_view/<book_id>', methods=["GET", "POST"])
@login_required
def book_view(book_id):
    # Connecting to the database
    db = sqlite3.connect('readroll.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Selecting the book to showcase based on book_id value
    cursor.execute("SELECT * FROM library WHERE user_id=? AND book_id=?", (session["user_id"], book_id))
    book = cursor.fetchall()
    book_info = [dict(i) for i in book]

    # Getting the book's name to display it in case the user wants to delete the book
    book_name = book_info[0]["book_name"]

    # Detecting form submission of deletion of the displayed book via the book's unique id in the database
    if request.method == 'POST':
        cursor.execute("DELETE FROM library WHERE user_id=? AND book_id=?", (session["user_id"], book_id))
        db.commit()
        flash(f"{book_name} has been deleted from your library.")
        return redirect('/library')

    return render_template("book_view.html", book_info=book_info[0])


# Display user's library
@app.route('/library', methods=["GET", "POST"])
@login_required
def library():
    # Connecting to the database
    db = sqlite3.connect('readroll.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Selecting everything from the logged user's library
    cursor.execute("SELECT * FROM library WHERE user_id=?", (session["user_id"],))
    lib = cursor.fetchall()
    library = [dict(i) for i in lib]

    # Search function, if it is not used, the library displays all of the books using the else statement
    if request.method == 'POST':

        # If the search query is empty, display the whole library
        if request.form.get('search-text') == '':
            return render_template('library.html', library=library)
        
        # Getting the data using the search query
        search_query = request.form.get("search-text")
        cursor.execute("SELECT * FROM library WHERE user_id=? AND book_name LIKE ? OR user_id=? AND authors LIKE ?", (session["user_id"], f'%{search_query}%', session["user_id"], f'%{search_query}%'))
        slib = cursor.fetchall()
        searched_library = [dict(i) for i in slib]
        return render_template('library.html', searched_library=searched_library)
    else:
        return render_template('library.html', library=library)


# Display user's history
@app.route('/history')
@login_required
def history():
    # Connect to the database
    db = sqlite3.connect('readroll.db')

    # Create rows which will help with making a dictionary to put it into a table
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Get the user's history data
    cursor.execute("SELECT * FROM history WHERE user_id=? ORDER BY date_added DESC", (session["user_id"],))
    lib = cursor.fetchall()

    # Create a dictionary out of the fetched data
    history = [dict(i) for i in lib]

    return render_template('history.html', history=history)


# Generate a random book
@app.route('/rolled/<genre>', methods=["GET", "POST"])
def rolled(genre):
    # Connect the database
    db = sqlite3.connect('readroll.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Get random book data
    while True:
        try:
            data = search_books(genre)
            book_count = len(data["items"])
            random_book_index = random.randint(0, book_count - 1)
            random_book = data["items"][random_book_index]["volumeInfo"]
            break
        # Catch the KeyError in case there is no "items" key in the retrieved dictionary
        except KeyError:
            continue

    # Put the data into separate variables
    book_title = random_book["title"]
    book_authors = random_book.get("authors", ["Unavaliable"])[0]
    book_date = random_book.get("publishedDate", "Unavaliable")
    book_pages = random_book.get("pageCount", "Unavaliable")
    book_publisher = random_book.get("publisher", "Unavaliable")
    book_description = random_book.get("description", "No description avaliable.")
    book_cover = ""
    # If there is no 'imageLinks' key, render a "NoBookCover" template image
    if "imageLinks" not in random_book:
        book_cover = "https://www.lse.ac.uk/International-History/Images/Books/NoBookCover.png"
    # This is to ensure that there is a 'thumbnail' key within the 'imageLinks' key, because sometimes it is not
    else:
        book_cover = random_book['imageLinks'].get('thumbnail', 'https://www.lse.ac.uk/International-History/Images/Books/NoBookCover.png')

    # If the user is logged in add the roll to their history and let them add a title to their library and save rolled books into their history
    if session.get("user_id"):
        # If there are more than 50 titles in the user's history, delete the first one to make space for the new title, if the history isn't full, just add the new title
        cursor.execute("SELECT position_id FROM history WHERE user_id=?", (session["user_id"],))
        positions = cursor.fetchall()
        if len(positions) > 50:
            cursor.execute("DELETE FROM history WHERE position_id=?", positions[0])
            cursor.execute("INSERT INTO history (book_name, author, user_id) VALUES (?, ?, ?)", (book_title, book_authors, session["user_id"]))
            db.commit()
        else:
            cursor.execute("INSERT INTO history (book_name, author, user_id) VALUES (?, ?, ?)", (book_title, book_authors, session["user_id"]))
            db.commit()

        # Adding the book to the temporary library to then have to possibility to add it to the library if the user decides to do it
        # This method is here to prevent the wrong book being added since the POST method in the form refreshes the webpage
        # Every time a new page is created, it generates a random book which makes the next book the target for the add to library trigger
        cursor.execute("SELECT COUNT(*) FROM temp_library WHERE user_id=?", (session["user_id"],))
        temp_books = cursor.fetchone()[0]
        cursor.execute("SELECT MIN(temp_id) + 1 FROM temp_library WHERE user_id=?", (session["user_id"],))
        min_temp_id = cursor.fetchone()[0]

        # This ensures that minimum temporary id is never None
        if min_temp_id is None:
            min_temp_id = 1

        # This prevents the temporary id from becoming higher than 3, it combats the autoincrementation of "MIN(temp_id) + 1"
        if min_temp_id >= 3:
            min_temp_id = 2

        # If the amount of books is more than 2, delete the oldest one and shift their place so that there are always 2
        if temp_books >= 2:
            cursor.execute("DELETE FROM temp_library WHERE temp_id = (SELECT MIN(temp_id) FROM temp_library) AND user_id = ?", (session["user_id"],))
            cursor.execute("UPDATE temp_library SET temp_id = 1 WHERE temp_id = 2 AND user_id = ?", (session["user_id"],))
            cursor.execute("INSERT INTO temp_library (temp_id, book_name, authors, book_cover, published_date, book_description, book_genre, book_publisher, book_pages, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (min_temp_id, book_title, book_authors, book_cover, book_date, book_description, genre, book_publisher, book_pages, session["user_id"]))
            db.commit()
        else:
            cursor.execute("INSERT INTO temp_library (temp_id, book_name, authors, book_cover, published_date, book_description, book_genre, book_publisher, book_pages, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (min_temp_id, book_title, book_authors, book_cover, book_date, book_description, genre, book_publisher, book_pages, session["user_id"]))
            db.commit()
        
        # Rolled book is added to the library using the temporary library
        cursor.execute("SELECT book_name FROM library WHERE user_id=?", (session["user_id"],))
        titles = cursor.fetchall()
        titles_list = [title[0] for title in titles]

        # Detecting whether the "add to library" button has been clicked via the form submission
        if request.method == "POST" and 'add-book' in request.form: 

            # Getting the title variable to check later whether it is already in the user's library
            cursor.execute("SELECT book_name FROM temp_library WHERE user_id=? AND temp_id=?", (session["user_id"], 1))
            title = cursor.fetchone()
            title = title["book_name"]

            # Getting necessary variables from the temporary library of the logged user
            cursor.execute("SELECT * FROM temp_library WHERE user_id=? AND temp_id=?", (session["user_id"], 1))
            temp_book = cursor.fetchall()
            temp_lib = [dict(i) for i in temp_book]
            temp_lib = temp_lib[0]
            temp_book_title = temp_lib["book_name"]
            temp_book_authors = temp_lib["authors"]
            temp_book_cover = temp_lib["book_cover"]
            temp_book_date = temp_lib["published_date"]
            temp_book_description = temp_lib["book_description"]
            temp_book_genre = temp_lib["book_genre"]
            temp_book_publisher = temp_lib["book_publisher"]
            temp_book_pages = temp_lib["book_pages"]

            # Checking whether the title is already in user's library and adding it if it is not there
            if title not in titles_list:
                cursor.execute("INSERT INTO library (book_name, authors, book_cover, published_date, book_description, book_genre, book_publisher, book_pages, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (temp_book_title, temp_book_authors, temp_book_cover, temp_book_date, temp_book_description, temp_book_genre, temp_book_publisher, temp_book_pages, session["user_id"]))
                db.commit()
                flash(f"{temp_book_title} has been added to your library.")
                return redirect('/library')
            else:
                flash(f"{title} is already in your library.")
                return render_template('rolled.html', genre=genre, book_title=temp_book_title, book_authors=temp_book_authors, book_description=temp_book_description, book_publisher=temp_book_publisher, book_date=temp_book_date, book_pages=temp_book_pages, book_cover=temp_book_cover)


    return render_template('rolled.html', genre=genre, book_title=book_title, book_authors=book_authors, book_description=book_description, book_publisher=book_publisher, book_date=book_date, book_pages=book_pages, book_cover=book_cover)


# Register user
@app.route('/register', methods=["GET", "POST"])
def register():
    db = sqlite3.connect('readroll.db')
    cursor = db.cursor()

    # Forget user_id
    session.clear()

    # If the user gains access through POST method, continue
    if request.method == "POST":
        # If there is no username input, render an apology
        if not request.form.get("username"):
            flash("Please enter your username and password.")
            return render_template("register.html")

        # If there is no password input, render an apology
        elif not request.form.get("password"):
            flash("Please enter your username and password.")
            return render_template("register.html")
        
        # If the password is shorter than 8 characters, render an apology
        elif len(request.form.get("password")) < 8:
            flash("Please enter a password that is 8 characters or longer.")
            return render_template("register.html")

        # If the password is not confirmed, render an apology
        elif not request.form.get("confirmation"):
            flash("Please confirm your password.")
            return render_template("register.html")

        # If the passwords do not match, render an apology
        elif request.form.get("confirmation") != request.form.get("password"):
            flash("Passwords do not match.")
            return render_template("register.html")

        # Necessary variables
        username = request.form.get("username")
        hashed_password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        # Check if the username already exists in the database
        cursor.execute("SELECT username FROM users WHERE username = :username", {"username": username})
        usernames = cursor.fetchall()
        if len(usernames) == 1:
            flash("Username is already registered.")
            return render_template("register.html")

        # Add the newly registered user to the database
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        db.commit()

        return redirect("/login")

    # If the user gains access through GET, send them to the registration form
    else:
        return render_template("register.html")

# Log user in
@app.route('/login', methods=["GET", "POST"])
def login():
    conn = sqlite3.connect('readroll.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter your username and password.")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter your username and password.")
            return render_template("login.html")

        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]

        # Ensure username exists and password is correct
        if len(results) != 1 or not check_password_hash(results[0]["password"], request.form.get("password")):
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = results[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# Log user out
@app.route('/logout')
@login_required
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
