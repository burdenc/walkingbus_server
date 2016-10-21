#!/usr/bin/python
from server import db, Parent, Child, app

with app.app_context():
    db.drop_all()
    db.create_all()
    parent = Parent(u'117926215976770287007', 'Julien', 'abc@xyz.com')
    #parent2 = Parent(u'106352513382912108134', 'Not Julien', 'xyz@abc.com')
    db.session.add(parent)
    #db.session.add(parent2)
    db.session.commit()
    
    child1 = Child('Timmy', parent.id)
    child2 = Child('Bobby', parent.id)
    #child3 = Child('Ross', parent2)
    db.session.add(child1)
    db.session.add(child2)
    #db.session.add(child3)
    db.session.commit()
    Parent.query.all()
