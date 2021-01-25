from flask import Flask, render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import string,random
import requests as req
from requests.exceptions import ConnectionError
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Urls(db.Model):
    id_ = db.Column('id_',db.Integer,primary_key=True)
    long = db.Column("long",db.String())
    short = db.Column('short',db.String(2))

    def __init__(self,long,short):
        self.long = long
        self.short = short

@app.before_first_request
def create_tables():
    db.create_all()

def shortnen_url():
    letters = string.ascii_letters
    while True:
        random_url = ''.join(random.choice(string.ascii_letters) for x in range(2))
        short_url = Urls.query.filter_by(short=random_url).first()
        if not short_url:
            return random_url

@app.route('/', methods=['POST','GET'])
def hello():
    if request.method == "POST":
        url_received = request.form["nm"]
        try:
            requ = req.get(url_received)
        except ConnectionError:
            error = True
            return render_template('home.html',err = error)
        else:
            print('Web site exists')
        found_url = Urls.query.filter_by(long=url_received).first()
        if found_url:
            return redirect(url_for('display_short_url' ,url=found_url.short))
        else:
            short_url = shortnen_url()
            new_url = Urls(url_received,short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for('display_short_url' , url=short_url))
    else:
        return render_template("home.html")

@app.route('/dis/<url>')
def display_short_url(url):
    return render_template('short.html',short_url_to_display=url)

@app.route('/<short_url>')
def redirecttion(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f"<h1>Url doesn't Exist</h1>"

if __name__ == '__main__':
    app.run(debug=True)