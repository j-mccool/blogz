from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import check_pw_hash, make_pw_hash
from app import app,db
from models import User,Blog,Logs


#we're going to log the user agent and ip address of those that attempt to register and log in
def log_attempt(ip, agent, username, result):
    ip = ip
    agent = agent
    username = username
    result = result
    log = Logs(ip, agent, username, result)
    db.session.add(log)
    db.session.commit()

#redirect to /login page if there is no active session
@app.before_request
def require_log():
    allowed_routes = ['signup', 'login', 'blog', 'index']
    if not ('username' in session or request.endpoint in allowed_routes):
        flash("Please log in first!", 'error')
        return redirect('/login')

#new index route to act as homepage, listing all usernames
@app.route('/')
def index():
    users = User.query.all()
    username = request.args.get('user')
    if not username:
        return render_template('index.html', users = users)
    else:
        user = User.query.filter_by(username=username).first()
        user_posts = Blog.query.filter_by(owner_id=user).order_by(Blog.post_date.desc()).all()
        return render_template('blog.html', posts=user_posts, user=user)

#main route that should display all posts: most recent first
@app.route('/blog')
def blog():
    #query DB; order by post_date descending, display all
    posts = Blog.query.order_by(Blog.post_date.desc()).all()
    #get the 'id' param from the string
    id = request.args.get('id')
    username = request.args.get('user')
    while id:
        blog=Blog.query.get(id)
        user = User.query.filter_by(id=blog.owner_id).first()
        return render_template('entry.html', blog=blog, author=user.username)
    while username:
        user = User.query.filter_by(username=username).first()
        user_posts = Blog.query.filter_by(owner_id=user.id).order_by(Blog.post_date.desc()).all()
        return render_template('blog.html', posts=user_posts, user=user)
    if not id and not username:
        return render_template('blog.html', posts=posts)

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

        if not error:    
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
        agent = request.headers.get('User-Agent')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

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
                result = 4
                log_attempt(ip, agent, username, result)
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
        agent = request.headers.get('User-Agent')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            result = 0
            log_attempt(ip, agent, username, result)
            flash('Logged In!', 'success')
            return redirect('/newpost')
        elif not user:
            result = 1
            log_attempt(ip, agent, username, result)
            flash('Username does not exist. Please try again!', 'error')
            return redirect('/login')
        else:
            result = 2
            log_attempt(ip, agent, username, result)
            flash('Incorrect password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('User successfully logged out!', 'success')
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
