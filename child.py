from flask import g

import request
import server as s

@request.RequestModel
class Child(s.db.Model):
  id = s.db.Column(s.db.Integer, primary_key=True)
  name = s.db.Column(s.db.String(80))
  status = s.db.Column(s.db.String(80))
  parent_id = s.db.Column(s.db.Integer, s.db.ForeignKey('parent.id'))

  post_fields = {
    'name' : str,
  }

  put_fields = {
    'name' : str,
    'status' : str
  }

  get_fields = ['id', 'name', 'status', 'parent_id']

  def __init__(self, name):
    self.name = name
    self.parent_id = g.user.id
    self.status = 'unknown'

  def __repr__(self):
    return '<Child %r>' % self.name
