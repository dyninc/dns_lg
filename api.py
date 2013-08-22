# Provide REST interface to data

#goal here is to use the same API as described here:
#https://github.com/bortzmeyer/dns-lg

from __future__ import print_function

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

import flask
import datetime, time
import sys
import string
import json, csv
import functools
import random

import look_glass

app = flask.Flask(__name__)

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
  """This method allows for Cross-origin resource sharing (CORS). It is used as
  a decorator for the route methods below."""
  if methods is not None:
      methods = ', '.join(sorted(x.upper() for x in methods))
  if headers is not None and not isinstance(headers, basestring):
      headers = ', '.join(x.upper() for x in headers)
  if not isinstance(origin, basestring):
      origin = ', '.join(origin)
  if isinstance(max_age, timedelta):
      max_age = max_age.total_seconds()

  def get_methods():
      if methods is not None:
          return methods

      options_resp = current_app.make_default_options_response()
      return options_resp.headers['allow']

  def decorator(f):
      def wrapped_function(*args, **kwargs):
          if automatic_options and request.method == 'OPTIONS':
              resp = current_app.make_default_options_response()
          else:
              resp = make_response(f(*args, **kwargs))
          if not attach_to_all and request.method != 'OPTIONS':
              return resp

          h = resp.headers

          h['Access-Control-Allow-Origin'] = origin
          h['Access-Control-Allow-Methods'] = get_methods()
          h['Access-Control-Max-Age'] = str(max_age)
          if headers is not None:
              h['Access-Control-Allow-Headers'] = headers
          return resp

      f.provide_automatic_options = False
      return update_wrapper(wrapped_function, f)
  return decorator

def rest_args(*args):
  """Parse the REST arguments for allowed arguments."""
  ret = []
  for arg in args:
    if arg == 'format':
      fmt = flask.request.args.get('format')
      if fmt is None:
        fmt = 'json'
      #TODO enable other types
      if fmt is not 'json':
        fmt = 'json'
      ret.append(fmt)
    elif arg == 'server':
      name_server = flask.request.args.get('server')
      if name_server is None or 'undefined' in name_server:
        name_server = ""
      ret.append(name_server)
    elif arg == 'flags':
      flags = str(flask.request.args.get('flags'))
      if flags is not None and 'undefined' not in flags:
        flags = flags.split(',')
      else:
        flags = ['RD']
      ret.append(flags)
    else:
      # default string param
      prmvalue = flask.request.args.get(arg)
      if prmvalue is None:
        prmvalue = ""

      ret.append(prmvalue)

  return ret

@app.route('/')
@crossdomain(origin='*')
def index():
  """Show something to user if they access app with no zone to query."""
  return "Dyn DNS Looking Glass. TODO - write some API documentation?"

@app.route('/favicon.ico/', methods=['GET',])
@crossdomain(origin='*')
def favicon():
  """This function handles when a user uses a web browser to access the LG
  directly."""
  return app.send_static_file("favicon.ico") 

@app.route('/<domain>/', methods=['GET', ])
@app.route('/<domain>/<query_type>/', methods=['GET', ])
@app.route('/<domain>/<query_type>/<query_class>/', methods=['GET', ])
@crossdomain(origin='*')
def handle_query(domain, query_type="A", query_class="IN"):
  """This method is our actual app. It parses rest arguments, and runs a query. It then packages the data and generates a response."""
  if domain is None:
    return "Domain field can not be empty."

  fmt, server, flags = rest_args('format', 'server', 'flags' );

  retData = look_glass.query(domain, query_type, query_class, server, flags)

  if fmt == 'json':
    if not retData is None:
      return flask.jsonify(retData)
    else:
      return "No returned data."
  else:
    return "Format not supported."

if __name__ == "__main__":
  """The applicaton entry point."""
  my_port = 8185
  if "--debug" in sys.argv:
    #this allows for the app to be run in a terminal window and output
    #its debug info.
    app.debug = True
    app.run(port=my_port)
    import logging
    app.logger.setlevel(loggin.INFO)
  else:
    app.run(port=my_port, host='0.0.0.0')

