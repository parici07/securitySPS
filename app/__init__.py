from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

@app.template_filter('datetimeformat')
def datetimeformat(value):
    return datetime.datetime.fromtimestamp(value).strftime('%d/%m/%Y')

@app.template_filter('ratingformat')
def ratingformat(value):
    return round(value, 1)

@app.template_filter('format_datetime')
def format_datetime(value):
    return value.strftime('%d/%m/%Y %I:%M %p')

@app.template_filter('format_date')
def format_date(value):
    return value.strftime('%d/%m/%Y')

@app.template_filter('search_post')
def search_post(value):
    return value[:20] + '...'

from app import routes, models