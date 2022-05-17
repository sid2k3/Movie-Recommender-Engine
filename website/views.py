from flask import Blueprint, current_app as app

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return "Home Page"


@views.route("/search/<movie_tmdbid>")
def search(movie_tmdbid):
    idx = app.data_manager.get_index_from_tmdbid(int(movie_tmdbid))

    return f"Search Results for {movie_tmdbid} \n {app.cbr.recommend(idx)}"
