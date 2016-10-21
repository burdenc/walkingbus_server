#!/usr/bin/python
from flask import Flask, abort, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
GOOGLE_CLIENT_ID = '378160880549-57b3ckh3mjj3gja4hsqrbanm23pl8gcd.apps.googleusercontent.com'

import endpoint

@app.route('/login')
def login():
  return redirect(url_for('static', filename='login.html'))

def main():
  endpoints_dict = {
    '/' : endpoint.IndexEndpoint,
    '/parent/<id>' : endpoint.ParentEndpoint,
    '/child/' : endpoint.ChildEndpoint,
    '/child/<id>' : endpoint.ChildIdEndpoint,
    '/register/' : endpoint.RegisterEndpoint
  }
  endpoint.register_endpoints(api, endpoints_dict)
  app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == "__main__":
  main()
