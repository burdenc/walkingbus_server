import request
import server as s

times = (
  'MONDAY_AM',
  'MONDAY_PM',
  'TUESDAY_AM',
  'TUESDAY_PM',
  'WEDNESDAY_AM',
  'WEDNESDAY_PM',
  'THURSDAY_AM',
  'THURSDAY_PM',
  'FRIDAY_AM',
  'FRIDAY_PM'
)

from child import Child

assoc_table = s.db.Table('time_to_child',
  s.db.Column('left_id', s.db.Integer, s.db.ForeignKey('timeslot.id')),
  s.db.Column('right_id', s.db.Integer, s.db.ForeignKey('child.id'))
)

@request.RequestModel
class TimeSlot(s.db.Model):
  __tablename__ = 'timeslot'
  id = s.db.Column(s.db.Integer, primary_key=True)
  group_id = s.db.Column(s.db.Integer, s.db.ForeignKey('group.id'))
  chaperone_id = s.db.Column(s.db.Integer, s.db.ForeignKey('parent.id'))
  chaperone = s.db.relationship('Parent')
  time = s.db.Column(s.db.Enum(*times))
  children = s.db.relationship('Child', secondary=assoc_table)

  get_fields = ['id', 'time', 'children', 'chaperone_id']

  def __init__(self, chaperone_id, time):
    self.chaperone_id = chaperone_id
    self.time = time

  def __repr__(self):
    return '<Time (%r, %r, %r, %r)' % (self.id, self.time, self.group_id, self.chaperone_id)
