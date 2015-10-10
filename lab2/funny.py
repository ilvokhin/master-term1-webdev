#! /usr/bin/env python
# -*- coding: utf-8 -*

from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash

from couchdbkit import Server, Document, StringProperty, IntegerProperty, \
  DateTimeProperty, StringListProperty, BooleanProperty, loaders

import uuid
import hashlib
import functools

# conf
DB = 'funny'
HOST='0.0.0.0'
DEBUG = True
SECRET_KEY = 'you shall not pass!'

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
  privileged = BooleanProperty()
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

def make_password_hash(salt, password):
  return hashlib.md5(salt + password).hexdigest()

def make_user_from_request(request):
  # we don't store real password for security reason
  salt = uuid.uuid4().hex
  password = make_password_hash(salt, request.form['password'])
  return User(username = request.form['username'],
    salt = salt,
    password = password,
    privileged = False,
    starred = [])

@app.before_request
def before_request():
  g.db = connect_db(app.config['DB'])

  User.set_db(g.db)
  Post.set_db(g.db)

@app.route('/')
def show_posts():
  posts = list(Post.view('posts/all'))
  return render_template('show_posts.html', posts = posts)

def login_required(f):
  @functools.wraps(f)
  def wrapped(*args, **kwargs):
    if not session.get('logged_in'):
      abort(401)
    return f(*args, **kwargs)
  return wrapped

def privileged_required(f):
  @functools.wraps(f)
  def wrapped(*args, **kwargs):
    if not session.get('privileged'):
      abort(403)
    return f(*args, **kwargs)
  return wrapped

@app.route('/add_post', methods = ['POST'])
@login_required
def add_post():
  new_post = make_post_from_request(request)
  g.db.save_doc(new_post)

  flash('New post was successfully created')
  return redirect(url_for('show_posts'))

@app.route('/edit_post/<id>', methods = ['GET', 'POST'])
@privileged_required
def edit_post(id):
  if not g.db.doc_exist(id):
    abort(404)

  post = Post.get(id)

  if request.method == 'POST':
    post.title = request.form['title']
    post.text = request.form['text']
    post.save()

    flash('Post was successfully updated')
    return redirect(url_for('show_posts'))

  return render_template('edit_post.html', post = post)

@app.route('/remove_post/<id>', methods = ['GET'])
@privileged_required
def remove_post(id):
  if not g.db.doc_exist(id):
    abort(404)
  Post.get(id).delete()

  flash('Post was successfully removed')
  return redirect(url_for('show_posts'))

@app.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():
  error = None
  if request.method == 'POST':
    if not request.form['username']:
      error = 'Empty username'
    elif not request.form['password'] or not request.form['confirm']:
      error = 'Empty password or confirm password field'
    elif request.form['password'] !=  request.form['confirm']:
      error = 'Passwords does not match'
    else:
      # looks like everything ok, check db
      username = request.form['username']
      password = request.form['password']
      user = list(User.view('users/by_username', key=username))
      if user:
        error = 'User already exists'
      else:
        new_user = make_user_from_request(request)
        g.db.save_doc(new_user)
        flash('You have successfully registered')
        return redirect(url_for('show_posts'))

  return render_template('sign_up.html', error = error)

@app.route('/login', methods = ['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    user = list(User.view('users/by_username', key=username))
    if not user:
      error = 'Invalid username'
    elif make_password_hash(user[0].salt, password) != user[0].password:
      error = 'Invalid password'
    else:
      session['logged_in'] = True
      session['privileged'] = user[0].privileged
      flash('You were logged in')
      return redirect(url_for('show_posts'))

  return render_template('login.html', error = error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  session.pop('privileged', None)
  flash('You were logged out')
  return redirect(url_for('show_posts'))

def main():
  app.run(host=app.config.get('HOST'))

if __name__ == "__main__":
  main()
