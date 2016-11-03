import request
import server as s

from timeslot import TimeSlot

@request.RequestModel
class Group(s.db.Model):
  id = s.db.Column(s.db.Integer, primary_key=True)
  timeslots = s.db.relationship('TimeSlot')

  get_fields = ['id', 'timeslots']

  post_fields = {}

  def __init__(self):
    pass

  def __repr__(self):
    return '<Group (%r, %r)' % (self.id, self.timeslots)
