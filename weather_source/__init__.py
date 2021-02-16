from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from weather_source.config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

import weather_source.routes