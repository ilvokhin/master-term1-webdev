#! /usr/bin/env python
# -*- coding: utf-8 -*

from wtforms import Form
from wtforms import TextField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import validators

def strip_filter(x):
  return x.strip() if x else None

class SignUpForm(Form):
  username = TextField \
  (
    'username', 
    [validators.Length(min=3, max=25)],
    filters = [strip_filter]
  )
  password = PasswordField \
  (
    'password',
    [
      validators.Required(),
      validators.EqualTo('confirm', message = 'Passwords must match.')
    ]
  )
  confirm = PasswordField('password', [validators.Required()]
    

class LoginForm(Form):
  username = TextField \
  (
    'username', 
    [validators.Length(min=3, max=25)],
    filters = [strip_filter]
  )
  password = PasswordField('password', [validators.Required()])

class PostForm(Form):
  title = TextField('title', [validators.Length(min=3)], filters = [strip_filter])
  text = TextField('text', [validators.Length(min=3)], filters = [strip_filter])
  tags = TextField('tags', [validators.Length(min=3)], filters = [strip_filter])
