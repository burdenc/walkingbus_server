import request
import server as s

from group import Group

assoc_table = s.db.Table('parent_to_group',
  s.db.Column('parent_id', s.db.Integer, s.db.ForeignKey('parent.id')),
  s.db.Column('group_id', s.db.Integer, s.db.ForeignKey('group.id'))
)

@request.RequestModel
class Parent(s.db.Model):
  id = s.db.Column(s.db.Integer, primary_key=True)
  google_id = s.db.Column(s.db.Text, unique=True)
  name = s.db.Column(s.db.String(80), unique=True)
  email = s.db.Column(s.db.String(120), unique=True)
  children = s.db.relationship('Child')
  groups = s.db.relationship('Group', secondary=assoc_table, backref='parents')

  get_fields = ['id', 'name', 'email', 'children', 'groups']

  def __init__(self, google_id, name, email):
    self.google_id = google_id
    self.name = name
    self.email = email

  def __repr__(self):
    return '<User (%r, %r)>' % (self.id, self.name)
