from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Password1!@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.static_folder = 'static'
app.secret_key = 'cCtWcZQi3JpjxGah6kErLkX4IYWpeQ0h'

db = SQLAlchemy(app)
