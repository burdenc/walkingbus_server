from flask import abort, g
from flask_restful import Resource

import auth
import request
import server as s

from child import Child
from parent import Parent

def register_endpoints(api, endpoint_dict):
  for path, endpoint in endpoint_dict.iteritems():
    api.add_resource(endpoint, path)

class IndexEndpoint(Resource):
  def get(self):
    return Parent.query.first().get()

class ParentEndpoint(auth.AuthParentResource):
  def get(self, id):
    return g.user.get()

class ChildEndpoint(auth.AuthUserResource):
  def post(self):
    child = Child.post()
    return child.get()

class ChildIdEndpoint(auth.AuthChildResource):
  def get(self, id):
    return g.child.get()

  def patch(self, id):
    g.child.patch()
    return g.child.get()

class RegisterEndpoint(Resource):
  def post(self):
    args = request.auth_parser.parse_args()
    token = args['Authentication']
    decrypted_token = auth.decrypt_google_token(token)
    if not decrypted_token:
      abort(401)

    user_id = decrypted_token['sub']

    # User already exists
    user = Parent.query.filter_by(google_id=user_id).first()
    if user:
      return user.get(), 202

    # User must have verified email
    if not decrypted_token['email_verified']:
      abort(403)

    new_parent = Parent(user_id, decrypted_token['name'], decrypted_token['email'])
    s.db.session.add(new_parent)
    s.db.session.commit()

    return new_parent.get()
