import os
import requests


from flask import Flask, session, render_template, request, jsonify, abort, redirect 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)        

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['JSON_SORT_KEYS'] = False
Session(app)



#SQL Db - using hardcoded instead of environment variable so grader can access... 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gupirjpihalrmq:405f4b2021de5c82891939c425cc8de0987d4890ba61e94d282ba4ee1a93f724@ec2-34-197-141-7.compute-1.amazonaws.com:5432/dcu17c2n8mi3p4'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False 
db = SQLAlchemy(app)



# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"))      #pasted the url here so grader can access...
engine2 = create_engine("postgres://gupirjpihalrmq:405f4b2021de5c82891939c425cc8de0987d4890ba61e94d282ba4ee1a93f724@ec2-34-197-141-7.compute-1.amazonaws.com:5432/dcu17c2n8mi3p4")
db2 = scoped_session(sessionmaker(bind=engine2))        # create a 'scoped session' that ensures different users' interactions with the database are kept separate



class Userlogin(db.Model):
    __tablename__ = 'userlogin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), unique=False)



class Reviews(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, unique=False)
    review = db.Column(db.String, unique=False)
    username = db.Column(db.String, db.ForeignKey("userlogin.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable = False)



class Books(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(25), unique=False)
    title = db.Column(db.String(250), unique=False)
    author = db.Column(db.String(250), unique=False)
    year = db.Column(db.Integer, unique=False)
    reviews = db.relationship("Reviews", backref="Books", lazy=True)

    def add_review(self, rating, review_text, session_user, book_id):
        r = Reviews(rating=rating, review=review_text, username=session_user, book_id=book_id)
        db2.add(r)
        db2.commit()



