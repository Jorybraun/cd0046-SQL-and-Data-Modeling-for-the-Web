import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# key  for csrf token
SECRET_KEY = 'ty4425hk54a21eee5719b9s9df7sdfklx'

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://udacity:udacity@localhost:5432/fyur'
