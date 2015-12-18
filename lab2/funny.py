#! /usr/bin/env python
# -*- coding: utf-8 -*

from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash

from database import connect_db, User, Post, make_post_from_request, \
  make_user_from_request, make_password_hash

from forms import SignUpForm, LoginForm, PostForm, format_form_errors

import functools

app = Flask(__name__)
app.config.from_object('config')

@app.before_request
def before_request():
  g.db = connect_db(app.config['DB'])

  User.set_db(g.db)
  Post.set_db(g.db)

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

@app.route('/', methods = ['GET', 'POST'])
def show_posts():
  form = PostForm(request.form)
  posts = list(Post.view('posts/by_date'))[::-1]
  errors = []
  if request.method == 'POST' and form.validate():
    new_post = make_post_from_request(request)
    g.db.save_doc(new_post)
    flash('New post was successfully created')
    return redirect(url_for('show_posts'))

  errors.extend(format_form_errors(form.errors.items()))
  return render_template \
    ('main.html', form = form, posts = posts, submit = 'Share', errors = errors)

@app.route('/tag/<tag>', methods = ['GET'])
def show_posts_tag(tag):
  posts = list(Post.view('posts/by_tag', key=tag))
  return render_template('posts.html', posts = posts)

@app.route('/starred', methods = ['GET'])
@login_required
def show_posts_starred():
  # I think it's not a good idea to use such implementation.
  user = User.get(session.get('uid'))
  posts = [elem for elem in Post.view('posts/by_date') if elem._id in user.starred]
  return render_template('posts.html', posts = posts)

@app.route('/edit_post/<id>', methods = ['GET', 'POST'])
@privileged_required
def edit_post(id):
  if not g.db.doc_exist(id):
    abort(404)

  form = PostForm(request.form)
  post = Post.get(id)
  errors = []

  if request.method == 'POST' and form.validate():
    post.title = form.title.data
    post.text = form.text.data
    post.tags = set(form.tags.data.split())
    post.save()
    flash('Post was successfully updated')
    return redirect(url_for('show_posts'))
  elif request.method == 'POST' and not form.validate():
    errors.extend(format_form_errors(form.errors.items()))
  elif request.method == 'GET':
    form.title.data = post.title
    form.text.data = post.text
    form.tags.data = ' '.join(post.tags)

  return render_template \
    ('edit_post.html', id = id, form = form, submit = 'Update', errors = errors)

@app.route('/remove_post/<id>', methods = ['GET'])
@privileged_required
def remove_post(id):
  if not g.db.doc_exist(id):
    abort(404)
  Post.get(id).delete()

  flash('Post was successfully removed')
  return redirect(url_for('show_posts'))

@app.route('/like_post/<id>', methods = ['GET'])
@login_required
def like_post(id):
  if not g.db.doc_exist(id):
    abort(404)
  post = Post.get(id)
  uid = session.get('uid')
  if uid not in post.likes:
    post.likes.add(uid)
  else:
    post.likes.remove(uid)
  post.save()
  return 'OK', 200, {'Content-Type': 'text/plain'}

@app.route('/star_post/<id>', methods = ['GET'])
@login_required
def star_post(id):
  if not g.db.doc_exist(id):
    abort(404)
  post = Post.get(id)
  uid = session.get('uid')
  user = User.get(uid)
  if uid not in post.stars:
    post.stars.add(uid)
    user.starred.add(post._id)
  else:
    post.stars.remove(uid)
    user.starred.remove(post._id)
  post.save()
  user.save()
  return 'OK', 200, {'Content-Type': 'text/plain'}

@app.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():
  errors = []
  form = SignUpForm(request.form)
  if request.method == 'POST' and form.validate():
    # looks like everything ok, check db
    username = form.username.data
    password = form.password.data
    user = list(User.view('users/by_username', key=username))
    if user:
      errors.append('User already exists')
    else:
      new_user = make_user_from_request(request)
      g.db.save_doc(new_user)
      flash('You have successfully registered')
      return redirect(url_for('show_posts'))
  elif request.method == 'POST' and not form.validate():
    errors.extend(format_form_errors(form.errors.items()))

  return render_template('sign_up.html', form = form, errors = errors)

@app.route('/login', methods = ['GET', 'POST'])
def login():
  errors = []
  form = LoginForm(request.form)
  if request.method == 'POST' and form.validate():
    username = form.username.data
    password = form.password.data
    user = list(User.view('users/by_username', key=username))
    if not user:
      errors.append('Invalid username')
    elif make_password_hash(user[0].salt, password) != user[0].password:
      errors.append('Invalid password')
    else:
      session['logged_in'] = True
      session['uid'] = user[0]._id
      session['privileged'] = user[0].privileged

      flash('You were logged in')
      return redirect(url_for('show_posts'))
  elif request.method == 'POST' and not form.validate():
    errors.extend(format_form_errors(form.errors.items()))

  return render_template('login.html', form = form, errors = errors)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  session.pop('uid', None)
  session.pop('privileged', None)

  flash('You were logged out')
  return redirect(url_for('show_posts'))

def main():
  app.run(host=app.config.get('HOST'))

if __name__ == "__main__":
  main()
