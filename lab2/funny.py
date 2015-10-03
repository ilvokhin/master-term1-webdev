#! /usr/bin/env python
# -*- coding: utf-8 -*

from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash

from couchdbkit import Server, Document, StringProperty, IntegerProperty, \
  DateTimeProperty, StringListProperty, loaders

# conf
DB_POSTS = 'posts'
DB_USERS = 'users'
HOST='0.0.0.0'
DEBUG = True
SECRET_KEY = 'you shall not pass!'
USERNAME = 'root'
PASSWORD = 'toor'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db(db_name):
  srv = Server()
  return srv.get_or_create_db(db_name)

def init_db(db_name):
  db = connect_db(db_name)
  loader = loaders.FileSystemDocsLoader('_design')
  loader.sync(db, verbose=True)

class User(Document):
  username = StringProperty()
  salt = StringProperty()
  password = StringProperty()
  role = StringProperty()
  starred = StringListProperty()

class Post(Document):
  author = StringProperty()
  title = StringProperty()
  text = StringProperty()
  like_cnt = IntegerProperty()
  star_cnt = IntegerProperty()
  date = DateTimeProperty()
  tags = StringListProperty()

def make_post_from_request(request):
  return Post(title = request.form['title'],
    text = request.form['text'],
    like_cnt = 0,
    star_cnt = 0)

@app.before_request
def before_request():
  g.db_users = connect_db(app.config['DB_USERS'])
  User.set_db(g.db_users)

  g.db_posts = connect_db(app.config['DB_POSTS'])
  Post.set_db(g.db_posts)

@app.route('/')
def show_posts():
  posts = Post.view('posts/all')
  return render_template('show_posts.html', posts = posts)

@app.route('/add_post', methods = ['POST'])
def add_post():
  if not session.get('logged_in'):
    abort(401)

  new_post = make_post_from_request(request)
  g.db_posts.save_doc(new_post)

  flash('New post was successfully created')
  return redirect(url_for('show_posts'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if request.form['username'] != app.config['USERNAME']:
      error = 'Invalid username'
    elif request.form['password'] != app.config['PASSWORD']:
      error = 'Invalid password'
    else:
      session['logged_in'] = True
      flash('You were logged in')
      return redirect(url_for('show_posts'))

  return render_template('login.html', error = error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('You were logged out')
  return redirect(url_for('show_posts'))

def main():
  app.run(host=app.config.get('HOST'))

if __name__ == "__main__":
  main()
