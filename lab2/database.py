#! /usr/bin/env python
# -*- coding: utf-8 -*

from couchdbkit import Server, Document, StringProperty, DateTimeProperty, \
  SetProperty, BooleanProperty, loaders

import uuid
import hashlib
import datetime

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
  starred = SetProperty()

class Post(Document):
  author = StringProperty()
  title = StringProperty()
  text = StringProperty()
  likes = SetProperty()
  stars = SetProperty()
  date = DateTimeProperty()
  tags = SetProperty()

def make_post_from_request(request):
  return Post(title = request.form['title'],
    text = request.form['text'],
    likes = set([]),
    stars = set([]),
    date = datetime.datetime.utcnow(),
    tags= set(request.form['tags'].split()))

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
