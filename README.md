# Web Programming with Python and JavaScript Project 1
<br>
A book review websdite written with the flask framework. This site allows site members to login in, search for a specific book, and write a review. More advanced users can use the API to gather information about a specific book. 
<br>
<br>
books.csv - A csv file with book information (isbn, title, author, year). This csv file will be imported into SQL table named "books". <br>
import.py - Interact with the SQL database. To create the SQL tables needed (books, reviews, userlogin). To insert books.csv into the SQL table books. <br>
application.py - The main flask application. Contains the website logic. <br>
models.py - Using ORM for some of the SQL task. <br>
<br>
/templates - Inside the templates directory lives html files for each of the webpages. <br>
api.html - contains the instructions for making API calls <br>
books.html - For users to search for a book based on isbn, book title, or author. <br>
books_reviews.html - The book review site. Users will be able to see other users reviews and average ratings (site users and goodreads users) <br>
layout.html - The template for this site. The nav bar is contained in there and extended to most other pages.  <br>
login.html - The login page. Username and Password required. <br>
register.html - The registration page. Username and Password must be entered. <br>
success.html - submit button in register page brings to success.html which then redirect to login.html. <br>
