import os
import sqlite3
import random

from functions import login_required, search_books
from flask import Flask, flash, render_template, redirect, session, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_url_path='/static')

db = sqlite3.connect('readroll.db')
cursor = db.cursor()

app.secret_key='admin12345'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/book_view', methods=["GET", "POST"])
@login_required
def book_view():
    return render_template("book_view.html")


@app.route('/library', methods=["GET", "POST"])
@login_required
def library():
    db = sqlite3.connect('readroll.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM library WHERE user_id=?", (session["user_id"],))
    lib = cursor.fetchall()
    library = [dict(i) for i in lib]

    if request.method == 'POST':
        if request.form.get('search-text') == '':
            return render_template('library.html', library=library)

        search_query = request.form.get("search-text")
        cursor.execute("SELECT * FROM library WHERE user_id=? AND book_name LIKE ? OR user_id=? AND author LIKE ?", (session["user_id"], f'%{search_query}%', session["user_id"], f'%{search_query}%'))
        slib = cursor.fetchall()
        searched_library = [dict(i) for i in slib]
        return render_template('library.html', searched_library=searched_library)
    else:
        return render_template('library.html', library=library)


@app.route("/history")
@login_required
def history():
    # Connect to the database and create 
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


@app.route('/rolled/<genre>', methods=["GET", "POST"])
def rolled(genre):
    # Connect the database
    db = sqlite3.connect('readroll.db')
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

    # If the user is logged in add the roll to their history and let them add a title to their library
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

        # Rolled book is added to the library
        cursor.execute("SELECT book_name FROM library WHERE user_id=?", (session["user_id"],))
        titles = cursor.fetchall()
        titles_list = [title[0] for title in titles]
        if request.method == "POST" and 'add-book' in request.form: 
            if book_title not in titles_list:
                cursor.execute("INSERT INTO library (book_name, author, book_cover, user_id) VALUES (?, ?, ?, ?)", (book_title, book_authors, book_cover, session["user_id"]))
                db.commit()
                flash(f"{book_title} has been added to your library.")
            else:
                flash(f"{book_title} is already in your library.")
            
    
    return render_template('rolled.html', genre=genre, book_title=book_title, book_authors=book_authors, book_description=book_description, book_publisher=book_publisher, book_date=book_date, book_pages=book_pages, book_cover=book_cover)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
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

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
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

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
