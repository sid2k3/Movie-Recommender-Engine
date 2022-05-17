from flask import Blueprint, current_app as app, render_template, url_for, flash
from flask_login import login_required, current_user

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/search/<movie_tmdbid>")
def search(movie_tmdbid):
    similar_movies = app.cbr_recommender(int(movie_tmdbid))
    print(similar_movies)
    return f"Search Results for {movie_tmdbid} \n {similar_movies}"
