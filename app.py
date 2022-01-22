from flask import Flask,render_template,request, redirect, url_for
import requests
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from newsapi import NewsApiClient

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'

db = SQLAlchemy(app)

def get_news(category):
    newsapi = NewsApiClient(api_key='587444a3c0ec46f7905e27bd682f895e')
    news = newsapi.get_top_headlines(category=category, language='en', country='in')
    return news


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=65b4781ff6eaf680ea0e3df496bb2fa2'
    json_object = requests.get(url).json()
    return json_object

@app.route('/')
def index_get():
    cities = City.query.all()
    weather_data = []
    for city in cities:
        
        json_object = get_weather_data(city.name)
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        
        icon = json_object['weather'][0]['icon']
        sunrise = datetime.utcfromtimestamp(int(json_object['sys']['sunrise']) + int(json_object['timezone']) ).strftime('%H:%M:%S')
        sunset = datetime.utcfromtimestamp(int(json_object['sys']['sunset']) + int(json_object['timezone']) ).strftime('%H:%M:%S')
        temperature = round( (float(json_object['main']['temp']) - 32) * 5.0/9.0 , 2)
        humidity = int(json_object['main']['humidity'])
        pressure = int(json_object['main']['pressure'])
        wind = int(json_object['wind']['speed'])
        desc = json_object['weather'][0]['description']

        weather = {
            'cityname': city.name,
            'icon': icon,
            'sunrise': sunrise,
            'sunset': sunset,
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
            'wind': wind,
            'desc': desc,
            'current_time': current_time
        }
        weather_data.append(weather)
    return render_template('home.html',weather_data=weather_data)


    
@app.route('/', methods=['POST'])
def index_post():
    new_city = request.form.get('city')
    new_city = new_city.capitalize() 
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)

            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()
        
    return redirect(url_for('index_get'))
    
@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    return redirect(url_for('index_get'))


@app.route('/general')
def index_get_general():
    news = get_news('general')
    return render_template('general.html',news=news)


@app.route('/entertainment')
def index_get_entertainment():
    news = get_news('entertainment')
    return render_template('entertainment.html',news=news)

@app.route('/business')
def index_get_business():
    news = get_news('business')
    return render_template('business.html',news=news)

@app.route('/health')
def index_get_health():
    news = get_news('health')
    return render_template('health.html',news=news)

@app.route('/science')
def index_get_science():
    news = get_news('science')
    return render_template('science.html',news=news)

@app.route('/sports')
def index_get_sports():
    news = get_news('sports')
    return render_template('sports.html',news=news)

@app.route('/technology')
def index_get_technology():
    news = get_news('technology')
    return render_template('technology.html',news=news)

if __name__ == '__main__':
    app.run(debug=True)



    