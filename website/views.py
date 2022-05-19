from flask import Blueprint, current_app as app, render_template, url_for, flash, request
from flask_login import login_required, current_user
from .models import Rating
from . import db
import json

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home():
    cfr_recommendations = app.get_recommendations_for_user(current_user.id, "cfr")
    cbr_recommendations = app.get_recommendations_for_user(current_user.id, "cbr")
    return render_template("home.html", cfr_recommendations=cfr_recommendations,
                           cbr_recommendations=cbr_recommendations)


@views.route("/search/<movie_tmdbid>")
@login_required
def search(movie_tmdbid):
    similar_movies = app.cbr_recommender(int(movie_tmdbid))
    print(similar_movies)
    return f"Search Results for {movie_tmdbid} \n {similar_movies}"


@views.route("/rate", methods=["GET", "POST"])
@login_required
def rate():
    if request.method == "POST":
        rating = int(request.form["rating"])
        movie_id = int(request.form["mid"])
        print(rating)
        print(movie_id)
        ratings_df = app.data_manager.actual_ratings

        # modifying rating if it already exists

        old_rating = Rating.query.filter_by(userId=current_user.id, tmdbId=movie_id).first()
        if old_rating:
            old_rating.rating = rating
            db.session.commit()
            ratings_df.loc[
                (ratings_df['userId'] == current_user.id) & (ratings_df['tmdbId'] == movie_id), 'rating'] = rating
            # Modifying existing rating in dataframe
        else:
            new_rating = Rating(rating=rating, tmdbId=movie_id, userId=current_user.id)
            db.session.add(new_rating)
            db.session.commit()
            ratings_df.loc[len(ratings_df.index)] = [current_user.id, movie_id, rating]
            # Adding new rating to the dataframe which is currently open in recommender engine

        print(ratings_df)

    return render_template("rate.html")


@views.route("/my_ratings", methods=["GET", "POST"])
@login_required
def show_ratings():
    ratings = []
    for rating in current_user.ratings:
        movie_title = app.data_manager.get_title_from_tmdbid(rating.tmdbId)
        ratings.append((movie_title, rating.rating))
    return render_template("my_ratings.html", ratings=ratings)
