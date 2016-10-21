from flask_restful import reqparse

import server as s

auth_parser = reqparse.RequestParser()
auth_parser.add_argument('Authentication',
                         required=True,
                         location=['headers', 'cookies', 'args'],
                         help='Authentication not provided')

item_parser = auth_parser.copy()
item_parser.add_argument('id',
                         type=int,
                         required=True,
                         location='view_args')

def RequestModel(cls):
  if hasattr(cls, 'put_fields'):
    cls.patch_parser = reqparse.RequestParser()
    for field, field_type in cls.put_fields.iteritems():
      cls.patch_parser.add_argument(field, type=field_type, store_missing=False)
    cls.patch = PATCH
  
  if hasattr(cls, 'get_fields'):
    cls.get = GET
  
  if hasattr(cls, 'post_fields'):
    cls.post_parser = reqparse.RequestParser()
    for field, field_type in cls.post_fields.iteritems():
      cls.post_parser.add_argument(field, type=field_type, store_missing=False)
    cls.post = classmethod(POST)

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
        if isinstance(v, s.db.Model):
          d[field].append(GET(v))
        else:
          d[field].append(v)
    
    else:
      if isinstance(val, s.db.Model):
        d[field] = GET(val)
      else:
        d[field] = val

  return d

def PATCH(row):
  args = row.patch_parser.parse_args()
  d = {}
  for field in row.put_fields:
    if field in args:
      setattr(row, field, args[field])

  s.db.session.commit()

def POST(model):
  args = model.post_parser.parse_args()
  d = {}
  for field in model.post_fields:
      if field in args:
        d[field] = args[field]

  new_row = model(**d)
  s.db.session.add(new_row)
  s.db.session.commit()
  return new_row
