from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Password1!@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form["body"]
    
        new_post = Blog(blog_title, blog_body)
        db.session.add(new_post)
        db.session.commit()

    posts = Blog.query.all()
    return render_template('blog.html', posts=posts)

if __name__ == '__main__':
    app.run()
