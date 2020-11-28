import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine2 = create_engine("postgres://gupirjpihalrmq:405f4b2021de5c82891939c425cc8de0987d4890ba61e94d282ba4ee1a93f724@ec2-34-197-141-7.compute-1.amazonaws.com:5432/dcu17c2n8mi3p4")
db2 = scoped_session(sessionmaker(bind=engine2))

    

""" Create the review table"""
def create_reviews():

    query = """     
                    CREATE TABLE reviews (
                    id SERIAL PRIMARY KEY,
                    rating int NOT NULL,
                    review VARCHAR NOT NULL,
                    username VARCHAR NOT NULL,
                    book_id INTEGER NOT NULL 
    ); """

    print(query)

    db2.execute(query)
    db2.commit()
    print("complete")


""" Create the user table"""
def create_userlogin():

    query = """     
                    CREATE TABLE userlogin (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR NOT NULL,
                    password VARCHAR NOT NULL
    ); """

    print(query)

    db2.execute(query)
    db2.commit()
    print("complete")



""" Create the user table"""
def create_books():

    query = """     
                    CREATE TABLE books (
                    id SERIAL PRIMARY KEY,
                    isbn VARCHAR NOT NULL,
                    title VARCHAR NOT NULL,
                    author VARCHAR NOT NULL,
                    year int NOT NULL
    ); """

    print(query)

    db2.execute(query)
    db2.commit()
    print("complete")


""" Insert books.csv into books table"""
def books_csv_insert():
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader) #skip header row. 
    
    #execute insert into, use : as placeholder; provide {dictionary} -> placeholder and fill in. 
    for isbn, title, author, year in reader: 
        print(isbn, title, author, year)
        db2.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})

        db2.commit()

#Use this to run one time queries... 
def custom_query():
    query = """     
                    DELETE FROM Reviews where username = 'bobby'
    """

    print(query)

    db2.execute(query)
    db2.commit()
    print("complete")

#uncomment to create tables etc, insert into table etc. 
if __name__ == "__main__":
    create_reviews()
    create_userlogin()
    create_books()
    books_csv_insert()
    #custom_query()
