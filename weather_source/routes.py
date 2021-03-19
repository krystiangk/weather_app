from .models import City
from . import app, db
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from datetime import datetime, timedelta
import flag
import requests

open_weather_app_id = app.config['OPEN_WEATHER_APP_ID']


def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={open_weather_app_id}'
    return requests.get(url).json()


@app.route('/')
def index_get():
    cities = City.query.order_by(City.datetime.desc()).all()
    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)

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
                .strftime('%Y-%m-%d %H:%M:%S'),
            'tz_sunset': (datetime.utcfromtimestamp(int(r['sys']['sunset'])) + timedelta(seconds=r['timezone']))
                .strftime('%Y-%m-%d %H:%M:%S'),
            'wind_speed': r['wind']['speed']
        }

        weather_data.append(weather)
        print(r)
    return render_template('weather.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    new_city = request.form.get('city').title()
    weather_city = get_weather_data(new_city)

    if weather_city['cod'] == '404':
        flash('Sorry, this city doesn\'t exist. Please choose another one.', 'info')
        return redirect(url_for('index_get'))

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            current_time = datetime.utcnow()
            new_city_obj = City(name=new_city, datetime=current_time)
            db.session.add(new_city_obj)
            db.session.commit()
        else:
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

