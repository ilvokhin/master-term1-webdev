#! /usr/bin/env python
# -*- coding: utf-8 -*

from wtforms import Form
from wtforms import TextField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import validators
from wtforms.widgets import TextArea

def strip_filter(x):
  return x.strip() if x else None

def format_form_errors(raw_errors):
  out = []
  for field, errors in raw_errors:
    for error in errors:
      error_msg = 'Error in field: %s - %s' % (field, error)
      out.append(error_msg)
  return out

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
  confirm = PasswordField('confirm', [validators.Required()])

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
  text = TextField('text', [validators.Length(min=3)], filters = [strip_filter], widget=TextArea())
  tags = TextField('tags', [validators.Length(min=3)], filters = [strip_filter])
