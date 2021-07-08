import requests
from mysql.connector import connect

def conn():
    con = connect(host='127.0.0.1', username='root', password='root', database='weather')
    cursor = con.cursor()
    return con,cursor
def close():
    con,cursor = conn()
    con.close()

def display_city():
    con,cursor = conn()
    cursor.execute('SELECT * FROM city')
    city = cursor.fetchall()
    close()
    return city

def insert_city(city_name):
    con, cursor = conn()
    query = f"INSERT INTO `city` (`city_name`) VALUES ('{city_name}');"
    cursor.execute(query)
    con.commit()
    cursor.close()
    con.close()

def delete_city(city_name):
    con, cursor = conn()
    query='DELETE FROM city WHERE CITY_NAME = "{}" '.format(city_name)
    cursor.execute(query)
    con.commit()
    cursor.close()
    con.close()

def get_weather_data(city):
    url=f'http://api.openweathermap.org/data/2.5/weather?q={city}&APPID=17ed68bedafbe09f90ffe63d9e3cb4ff'
    r = requests.get(url).json()
    return(r)

from flask import Flask, render_template , request ,redirect,url_for,flash

app = Flask(__name__)
app.config['SECRET_KEY']='thisisasecret'

@app.route("/")
def index_get():
    city_data=(display_city())
    weather_data=[]
    for city in city_data:
        r=get_weather_data(city[1])
        weather={
            'city' :city[1],
            'temp' :r['main']['temp'],
            'des' :r['weather'][0]['description'],
            'icon' :r['weather'][0]['icon'],
        }
        weather_data.append(weather)
    return render_template('weather.html',weather_data=weather_data)


@app.route("/",methods=['POST'])
def index_post():
    err=''
    if (request.method == 'POST'):
        new_city=(request.form['city'])
        city_data = (display_city())
        if new_city:
            city_list = []
            for city in city_data:
                city_list.append(city[1])
            if new_city not in city_list:
                new_city_data = get_weather_data(new_city)
                print(new_city_data)
                if new_city_data['cod'] == 200:
                    insert_city(new_city)
                else:
                    err ='City doesnt exists in the world'
            else:
                err = 'City already exists in database'
    if err:
        flash(err , 'error')
    else:
        flash('City added successfully!')
    return redirect(url_for('index_get'))


@app.route("/delete/<string:city_name>")
def delete(city_name):
    delete_city(city_name)
    flash(f'Successfully deleted {city_name}' , 'success')
    return redirect("/")