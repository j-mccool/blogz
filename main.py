from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Password1!@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.static_folder = 'static'
app.secret_key = 'cCtWcZQi3JpjxGah6kErLkX4IYWpeQ0h'

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    post_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, post_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if post_date is None:
            post_date = datetime.utcnow()
        self.post_date = post_date
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Logs(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20))
    agent = db.Column(db.String(500))
    username = db.Column(db.String(120))
    password = db.Column(db.String(30))
    success = db.Column(db.Boolean)

    def __init__(self, ip, agent, username, password, success):
        self.ip = ip
        self.username = username
        self.password = password
        self.agent = agent
        self.success = False

#redirect to /login page if there is no active session
@app.before_request
def require_log():
    allowed_routes = ['signup', 'login', 'blog', 'index']
    if not ('username' in session or request.endpoint in allowed_routes):
        flash("Please log in first!", 'error')
        return redirect('/login')

#main route that should display all posts: most recent first
@app.route('/blog')
def blog():
    #query DB; order by post_date descending, display all
    posts = Blog.query.order_by(Blog.post_date.desc()).all()
    #get the 'id' param from the string
    id = request.args.get('id')
    if not id:
        return render_template('blog.html', posts=posts)
    else:
        #if there is an 'id' param, display a single post on the entry page
        blog = Blog.query.get(id)
        return render_template('entry.html', blog=blog)

#newpost route that should allow a person to enter a new post
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form["body"]
        error = ''
        

        if blog_title == '':
            error = 'yes'
            flash("Please enter a title.", 'error')
        if blog_body == '':
            error = 'yes'
            flash("Please enter some text for your post.", 'error')

        if not error and not error:    
            new_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()
            newest_post = db.session.query(Blog).order_by(Blog.id.desc()).first()
            id = str(newest_post.id)
            return redirect("/blog?id=" + id)
        else:
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, error=error)
    else:
        return render_template('newpost.html')
#signup route - username/pword must be > 3, passwords must match, username/pword can't be null
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        error = ''
        #validation for signup; if error set value, create flash message with category
        if (len(password) < 3) or (len(username) < 3):
            error = 'yes'
            flash('Fields must be more than 3 characters. Please re-enter.', 'error')
        if username == '' or password== '':
            error = 'yes'
            flash('Field cannot be null', 'error')
        if verify != password:
            error = 'yes'
            flash('Password and Verify fields must match. Please try again.', 'error')
        if not error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash('New User Created - Logged In!', 'success')
                return redirect('/newpost')
            else:
                flash('Oops! Looks like we already have a user by that name.', 'error')
                return render_template('signup.html', username=username, error=error)
        else:
            return render_template('signup.html', username=username)
    return render_template('signup.html')

#login route; if post, and if user exists and password is correct log in to /newpost, else display error
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged In!', 'success')
            return redirect('/newpost')
        elif not user:
            flash('Username does not exist. Please try again!', 'error')
            return redirect('/login')
        else:
            flash('Incorrect password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('User successfully logged out!', 'success')
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
