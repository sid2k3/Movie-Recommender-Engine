from flask import Blueprint, current_app as app, render_template, url_for, flash, request, redirect
from flask_login import login_required, current_user
from .models import Rating
from . import db
import json

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home():
    all_movies = app.data_manager.get_all_movies()
    print(all_movies)
    cfr_recommendations = app.get_recommendations_for_user(current_user.id, "cfr")
    cbr_recommendations = app.get_recommendations_for_user(current_user.id, "cbr")
    return render_template("home.html", cfr_recommendations=cfr_recommendations,
                           cbr_recommendations=cbr_recommendations, movies=all_movies)


@views.route("/search/<movie_tmdbid>")
@login_required
def search(movie_tmdbid):
    similar_movies = app.cbr_recommender(int(movie_tmdbid))
    print(similar_movies)
    return f"Search Results for {movie_tmdbid} \n {similar_movies}"


#
# @views.route("/rate", methods=["GET", "POST"])
# @login_required
# def rate():
#     if request.method == "POST":


@views.route("/ratings", methods=["GET", "POST"])
@login_required
def ratings():
    if request.method == "GET":
        user_ratings = []
        for rating in current_user.ratings:
            movie_info = app.data_manager.get_details_from_tmdbid(rating.tmdbId)
            user_ratings.append((movie_info, rating.rating))
        return render_template("my_ratings.html", ratings=user_ratings)
    else:
        print(request.form)
        movie_id = int(request.form["tmdbId"])

        operation_type = request.form["type"]
        ratings_df = app.data_manager.actual_ratings
        if operation_type == "add":
            rating = int(request.form["stars"])

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

            flash("Rating Submitted Successfully", category="info")

        elif operation_type == "delete":
            old_rating = Rating.query.filter_by(userId=current_user.id, tmdbId=movie_id).first()
            if old_rating:
                db.session.delete(old_rating)
                db.session.commit()
                ratings_df.drop(ratings_df.loc[
                                    (ratings_df['userId'] == current_user.id) & (
                                            ratings_df['tmdbId'] == movie_id)].index, inplace=True)

                flash("Rating Deleted Successfully", category="info")
        print(ratings_df)
        return redirect(request.form["redirect_url"])
