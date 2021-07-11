from os import name
from flask import Flask, render_template, request
from flask import url_for, redirect
from flask.typing import URLDefaultCallable
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICAIONS'] = False

db = SQLAlchemy(app)


class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(3))

    def __init__(self, long, short):
        self.long = long
        self.short = short


@app.before_first_request
def create_tables():
    db.create_all()


def shorten_url():
    letters = string.ascii_letters
    while True:
        rand_letters = random.choices(letters, k=5)
        rand_letters = "".join(rand_letters)
        short_url = Urls.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        url_rec = request.form["nm"]
        url_shortname = request.form["shortname"]

        if url_shortname != "":
            found_url = Urls.query.filter_by(long=url_rec).first()
            if found_url:
                return redirect(url_for("display", url=found_url.short))
            else:
                short_url = url_shortname
                new_url = Urls(url_rec, short_url)
                db.session.add(new_url)
                db.session.commit()
                return redirect(url_for("display", url=short_url))

        else:
            found_url = Urls.query.filter_by(long=url_rec).first()
            if found_url:
                return redirect(url_for("display", url=found_url.short))
            else:
                short_url = shorten_url()
                new_url = Urls(url_rec, short_url)
                db.session.add(new_url)
                db.session.commit()
                return redirect(url_for("display", url=short_url))

    else:
        return render_template('home.html')


@app.route('/display/<url>')
def display(url):
    return render_template('shorturl.html', short_url_display=url)


@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1> URl doesnt exist </h1>'


@app.route('/allurl')
def all():
    return render_template('allurl.html', vals=Urls.query.all())


if __name__ == '__main__':
    app.run(port=5000, debug=True)
