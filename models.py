from app import db
from datetime import datetime
from hashutils import check_pw_hash, make_pw_hash

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
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

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


class Logs(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20))
    agent = db.Column(db.String(500))
    username = db.Column(db.String(120))
    result = db.Column(db.Integer)

    def __init__(self, ip, agent, username, result):
        self.ip = ip
        self.username = username
        self.agent = agent
        self.result = result
