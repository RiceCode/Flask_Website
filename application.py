import os
import requests

from flask import Flask, session, render_template, request, jsonify, abort, redirect 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy

from models import * 


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['JSON_SORT_KEYS'] = False
Session(app)


#API Key for goodreads
APIKEY_BOOK = "heiWvgsAFGVXw8Jeb6QUw"


#SQL Db - using hardcoded instead of environment variable so grader can access... 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gupirjpihalrmq:405f4b2021de5c82891939c425cc8de0987d4890ba61e94d282ba4ee1a93f724@ec2-34-197-141-7.compute-1.amazonaws.com:5432/dcu17c2n8mi3p4'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False 
db = SQLAlchemy(app)


@app.route("/")
def index():
    #ensure user is logged in; otherwise redirect them to login page
    if not session:
        return redirect("/login")
    return redirect("/books")


@app.route("/register")
def register():
    return render_template('register.html')


#Allows user to login and creates a session under that username. Redirects to books if success. 
#if user already exist. 
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']    

        #If username + password is correct, it'll return that row. Then create a session using that username. 
        login = db2.execute("SELECT * FROM userlogin WHERE username = :username and password = :password", {"username": username, "password": password}).fetchone()
        if login:
            session["username"] = username
            return redirect("/books")
        else: 
            return render_template('login.html', message="Incorrect password. Please try again or call the police.")
    else: 
        return render_template('login.html')




#After login, redirect to book
@app.route("/books", methods=['POST', 'GET'])
def book():
    #ensure user is logged in; otherwise redirect them to login page
    if not session:
        return redirect("/login")


    #user select dropdown (isbn, book, author). Return all and partial choices. 
    results = ""
    if request.method == 'POST' and session:
        #Get the user inputs. 
        search_text = request.form['search']
        search_text = search_text.upper()
        book_option = request.form['book_option']     

        #SQL result 
        if book_option == "title": 
            results = db2.execute("SELECT * FROM books WHERE UPPER(title) like :user_answer", {"user_answer": "%"+search_text+"%"}).fetchall()
        elif book_option == "author":
            results = db2.execute("SELECT * FROM books WHERE UPPER(author) like :user_answer", {"user_answer": "%"+search_text+"%"}).fetchall()
        elif book_option == "isbn":
            results = db2.execute("SELECT * FROM books WHERE UPPER(isbn) like :user_answer", {"user_answer": "%"+search_text+"%"}).fetchall()

    return render_template("books.html", results=results, username=session["username"])


def get_review_data(book_id, session_username):
    book_info = db2.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchone()

    #Check if user posted review 
    user_posted = db2.execute("SELECT * FROM reviews WHERE username = :username AND book_id = :bookid", {"username": session_username, "bookid": book_id}).fetchone()

    #Get all the review of this book by other users
    other_reviews = db2.execute("SELECT * FROM reviews WHERE username != :username AND book_id = :bookid", {"username": session_username, "bookid": book_id}).fetchall()
    if user_posted is None: 
        user_posted = ""

    #Get this book's average rating from this site
    user_avg_rating = db2.execute("SELECT ROUND(avg(rating),2) FROM reviews WHERE book_id = :bookid", {"bookid": book_id}).fetchone()[0]
    if user_avg_rating is None: 
        user_avg_rating = "None"

    return(book_info, user_posted, other_reviews, user_avg_rating)


#Review Page
@app.route("/books/<string:book_id>", methods=['POST', 'GET'])
def book_detail(book_id):
    #Ensure user is logged in
    if not session:
        return redirect("/login")

    #get the book info, user's review and other people's review. 
    book_info, user_posted, other_reviews, user_avg_rating = get_review_data(book_id, session["username"])

    #Goodreads-API-data
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": APIKEY_BOOK, "isbns": book_info.isbn}).json()
    goodreads_rating = res['books'][0]['average_rating']

    #When user lands on the webpage
    if request.method == 'GET':
        return render_template("books_review.html", book_info=book_info, username=session["username"],
            previous_review=user_posted, other_reviews=other_reviews, goodreads_rating=goodreads_rating, user_avg_rating=user_avg_rating)
                
    #When user enters new review. First delete previous review then insert new review. 
    elif request.method == 'POST': 
        user_review_text = request.form['review_text']
        user_rating_score = request.form['rating_score']
 
        #Delete old review from user. 
        if user_posted: 
            db2.execute("DELETE FROM reviews WHERE username = :username AND book_id = :bookid", {"username": session["username"], "bookid": book_id})
            db2.commit()

        #Insert new review from user
        new_review = Books.query.get(book_id)
        new_review.add_review(rating=user_rating_score, review_text=user_review_text, session_user=session["username"], book_id=book_id)

        #Get the latest update
        book_info, user_posted, other_reviews, user_avg_rating = get_review_data(book_id, session["username"])

        return render_template("books_review.html", book_info=book_info, username=session["username"],
            previous_review=user_posted, other_reviews=other_reviews, goodreads_rating=goodreads_rating, user_avg_rating=user_avg_rating)



@app.route("/submit", methods=['POST']) 
def submit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']    

        #Allow username if it is not empty or if it isn't taken already.
        if username == '':
            return render_template('register.html', message="Please enter a username")
        #if returns = username already exists. 
        elif db2.execute("SELECT * FROM userlogin WHERE username = :username", {"username": '%'+username+'%'}).fetchone():
            return render_template('register.html', message="Username already exists; Please choose a new username")
        #new try: 
        else: 
            db2.execute("INSERT INTO userlogin (username, password) VALUES (:username, :password)",
                    {"username": username, "password": password})

            db2.commit() 
            #return render_template('success.html')
            return redirect("/login")
        



@app.route("/logout")
def logout():
    session.pop("username", None)

    return redirect("/")




#After login, redirect to book
@app.route("/api")
def api():
    #ensure user is logged in; otherwise redirect them to login page
    if not session:
        return redirect("/login")

    return render_template("api.html")





#API Page for API calls
@app.route("/api/books/<string:isbn_nbr>")
def api_query(isbn_nbr):

    book = Books.query.filter_by(isbn=isbn_nbr).first()

    if book is None:
        return jsonify({"error": "No such book"}), 404

    avg_rating = db2.execute("SELECT ROUND(avg(rating),2) FROM reviews WHERE book_id = :bookid", {"bookid": book.id}).fetchone()[0]
    num_review = db2.execute("SELECT COUNT(id) FROM reviews WHERE book_id = :bookid", {"bookid": book.id}).fetchone()[0]

    if avg_rating is None:
        avg_rating = 0.0
    
    return jsonify({
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "average_score": float(avg_rating),
        "review_count": num_review
    })
    








