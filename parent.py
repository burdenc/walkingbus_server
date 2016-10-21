import request
import server as s

@request.RequestModel
class Parent(s.db.Model):
  id = s.db.Column(s.db.Integer, primary_key=True)
  google_id = s.db.Column(s.db.Text, unique=True)
  name = s.db.Column(s.db.String(80), unique=True)
  email = s.db.Column(s.db.String(120), unique=True)
  children = s.db.relationship('Child')

  get_fields = ['id', 'name', 'email', 'children']

  def __init__(self, google_id, name, email):
    self.google_id = google_id
    self.name = name
    self.email = email

  def __repr__(self):
    return '<User (%r, %r)>' % (self.id, self.name)
