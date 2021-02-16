import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import flag
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
open_weather_app_id = os.getenv('OPEN_WEATHER_APP_ID')


def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={open_weather_app_id}'
    r = requests.get(url).json()
    return r


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.DateTime)


@app.route('/')
def index_get():
    cities = City.query.order_by(City.datetime.desc()).all()

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'

    weather_data = []

    for city in cities:

        r = requests.get(url.format(city.name, open_weather_app_id)).json()
        print(r)
        print(open_weather_app_id)
        weather = {
            'city': city.name,
            'country': r['sys']['country'],
            'flag': flag.flag(r['sys']['country']),
            'temperature': r['main']['temp'],
            'description': (r['weather'][0]['description']).title(),
            'pressure': r['main']['pressure'],
            'icon': r['weather'][0]['icon'],
            'lon': r['coord']['lon'],
            'lat': r['coord']['lat'],
            'humidity': r['main']['humidity'],
            'sunrise': r['sys']['sunrise'],
            'sunset': r['sys']['sunset'],
            'offset': r['timezone'],
            'tz_sunrise':  (datetime.utcfromtimestamp(int(r['sys']['sunrise']))+timedelta(seconds=r['timezone']))
                .strftime('%H:%M:%S'),
            'tz_sunset': (datetime.utcfromtimestamp(int(r['sys']['sunset'])) + timedelta(seconds=r['timezone']))
                .strftime('%H:%M:%S'),
            'wind_speed': r['wind']['speed']
        }

        weather_data.append(weather)
        print(r)
    return render_template('weather.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city').title()

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            current_time = datetime.utcnow()
            new_city_obj = City(name=new_city, datetime=current_time)
            db.session.add(new_city_obj)
            db.session.commit()
        else:
            err_msg = 'City already exists!'
            flash('This city already exists in the database. Please choose another one.', 'info')
        return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete_city(name):
    city_to_delete = City.query.filter_by(name=name).first()
    db.session.delete(city_to_delete)
    db.session.commit()
    flash('City successfully deleted', 'success')
    return redirect(url_for('index_get'))


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()