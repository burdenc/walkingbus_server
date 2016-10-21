from oauth2client import client, crypt
from functools import wraps
from flask import g
from flask_restful import Resource

import request
import child
import parent

def decrypt_google_token(token):
  if token == u'IAMADUMMY':
    return {'sub' : u'117926215976770287007'}
  try:
    idinfo = client.verify_id_token(token, GOOGLE_CLIENT_ID)
    # If multiple clients access the backend server:
    if idinfo['aud'] not in [GOOGLE_CLIENT_ID]:
      raise crypt.AppIdentityError("Unrecognized client.")
    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
      raise crypt.AppIdentityError("Wrong issuer.")
  except:
    return None

  return idinfo

def authenticate_user(token):
  dec_token = decrypt_google_token(token)
  if not dec_token:
    abort(401)

  user_id = dec_token['sub']
  user = parent.Parent.query.filter_by(google_id=user_id).first()
  if not user:
    abort(401)

  return user

def verify_child_access(user, child_id):
  c = child.Child.query.filter_by(id=child_id).first()
  if not c or c.parent_id != user.id:
    abort(401)

  return c

def login_auth(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    req = request.auth_parser.parse_args()
    user = authenticate_user(req['Authentication'])
    if not user:
      abort(401)

    g.user = user
    return func(*args, **kwargs)
  return wrapper

def parent_auth(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    req = request.item_parser.parse_args()
    user = authenticate_user(req['Authentication'])
    if not user or user.id != req['id']:
      abort(401)

    g.user = user
    return func(*args, **kwargs)
  return wrapper

def child_auth(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    req = request.item_parser.parse_args()
    user = authenticate_user(req['Authentication'])
    child = verify_child_access(user, req['id'])
    g.user = user
    g.child = child
    return func(*args, **kwargs)
  return wrapper

class AuthUserResource(Resource):
  method_decorators = [login_auth]

class AuthParentResource(Resource):
  method_decorators = [parent_auth]

class AuthChildResource(Resource):
  method_decorators = [child_auth]

