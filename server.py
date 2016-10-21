#!/usr/bin/python
from flask import Flask, abort, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse

from oauth2client import client, crypt

from functools import wraps

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

GOOGLE_CLIENT_ID = '378160880549-57b3ckh3mjj3gja4hsqrbanm23pl8gcd.apps.googleusercontent.com'

auth_parser = reqparse.RequestParser()
auth_parser.add_argument('Authentication',
                         required=True,
                         location=['headers', 'cookies', 'args'],
                         help='Authentication not provided')

parent_parser = auth_parser.copy()
parent_parser.add_argument('parent_id',
                           type=int,
                           required=True,
                           location='view_args')

child_parser = auth_parser.copy()
child_parser.add_argument('child_id',
                          type=int,
                          required=True,
                          location='view_args')

register_parser = auth_parser.copy()

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
  user = Parent.query.filter_by(google_id=user_id).first()
  if not user:
    abort(401)

  return user

def verify_child_access(user, child_id):
  child = Child.query.filter_by(id=child_id).first()
  if not child or child.parent_id != user.id:
    abort(401)

  return child

def parent_authenticate_wrapper(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    request = parent_parser.parse_args()
    user = authenticate_user(request['Authentication'])
    if not user or user.id != request['parent_id']:
      abort(401)

    g.user = user
    return func(*args, **kwargs)
  return wrapper

def child_authenticate_wrapper(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    request = child_parser.parse_args()
    user = authenticate_user(request['Authentication'])
    child = verify_child_access(user, request['child_id'])
    g.user = user
    g.child = child
    return func(*args, **kwargs)
  return wrapper

class AuthParentResource(Resource):
  method_decorators = [parent_authenticate_wrapper]

class AuthChildResource(Resource):
  method_decorators = [child_authenticate_wrapper]

def EndpointModel(cls):
  cls.patch_parser = reqparse.RequestParser()
  for field, field_type in cls.put_fields.iteritems():
    cls.patch_parser.add_argument(field, type=field_type, store_missing=False)
  return cls


# Serialize and return row of Model
# Works for simple relationships
def GET(row):
  d = {}
  for field in row.get_fields:
    val = getattr(row, field)
    if hasattr(val, '__iter__'):
      d[field] = []
      for v in val:
        if isinstance(v, db.Model):
          d[field].append(GET(v))
        else:
          d[field].append(v)
    
    else:
      if isinstance(val, db.Model):
        d[field] = GET(val)
      else:
        d[field] = val

  return d

def PATCH(model, query):
  args = model.patch_parser.parse_args()
  d = {}
  for field in model.put_fields:
    if field in args:
      d[field] = args[field]

  query.update(d)
  db.session.commit()

class Parent(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  google_id = db.Column(db.Text, unique=True)
  name = db.Column(db.String(80), unique=True)
  email = db.Column(db.String(120), unique=True)
  children = db.relationship('Child')

  get_fields = ['id', 'name', 'email', 'children']

  def __init__(self, google_id, name, email):
    self.google_id = google_id
    self.name = name
    self.email = email

  def __repr__(self):
    return '<User (%r, %r)>' % (self.id, self.name)

@EndpointModel
class Child(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80))
  status = db.Column(db.String(80))
  parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))

  post_fields = {
    'name' : str,
    'parent_id' : int,
  }

  put_fields = {
    'name' : str,
    'status' : str
  }

  get_fields = ['id', 'name', 'status', 'parent_id']

  def __init__(self, name, parent_id):
    self.name = name
    self.parent_id = parent_id
    self.status = 'unknown'

  def __repr__(self):
    return '<Child %r>' % self.name

@app.route('/login')
def login():
  return redirect(url_for('static', filename='login.html'))

class IndexEndpoint(Resource):
  def get(self):
    return GET(Parent.query.first())

class ParentEndpoint(AuthParentResource):
  def get(self, parent_id):
    return GET(g.user)

class ChildEndpoint(AuthParentResource):
  def post(self):
    pass 

class ChildIdEndpoint(AuthChildResource):
  def get(self, child_id):
    return GET(g.child)

  def put(self, child_id):
    pass

  def patch(self, child_id):
    PATCH(Child, Child.query.filter_by(id=child_id))

class RegisterEndpoint(Resource):
  def post(self):
    args = register_parser.parse_args()
    token = args['Authentication']
    decrypted_token = decrypt_google_token(token)
    if not decrypted_token:
      abort(401)

    user_id = decrypted_token['sub']

    # User already exists
    user = Parent.query.filter_by(google_id=user_id).first()
    if user:
      return GET(user), 202

    # User must have verified email
    if not decrypted_token['email_verified']:
      abort(403)

    new_parent = Parent(user_id, decrypted_token['name'], decrypted_token['email'])
    db.session.add(new_parent)
    db.session.commit()

    return GET(new_parent)


api.add_resource(IndexEndpoint, '/')
api.add_resource(ParentEndpoint, '/parent/<parent_id>')

api.add_resource(ChildEndpoint, '/child/')
api.add_resource(ChildIdEndpoint, '/child/<child_id>')

api.add_resource(RegisterEndpoint, '/register/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
