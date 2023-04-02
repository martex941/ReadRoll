import os
import requests
import random

from flask import redirect, session
from functools import wraps



def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def search_books(query):
    try:
        api_key = "AIzaSyAjyEIryt6W4DYRj8T_9SerZL7LuExUiTM"
        page_size = 10
        random_start_index = random.randint(0, page_size)
        url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{query}&startIndex={random_start_index}&maxResults={page_size}&langRestrict=en&country=US&key={api_key}'
        response = requests.get(url)
        data = response.json()
        return data
    except requests.RequestException:
        return None
