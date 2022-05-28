from flask import Blueprint, current_app as app, render_template, flash, request, redirect
from flask_login import login_required, current_user
from .models import Rating
from . import db

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home():
    all_movies = app.data_manager.get_all_movies()

    recommendations = app.get_recommendations_for_user(current_user.id)

    return render_template("home.html", recommendations=recommendations, movies=all_movies)


@views.route("/search/<movie_tmdbid>")
@login_required
def search(movie_tmdbid):
    similar_movies = app.cbr_recommender(int(movie_tmdbid))

    return render_template('search_results.html', similar_movies=similar_movies, length=len(similar_movies))


@views.route("/genre/<genre>")
@login_required
def search_genre(genre: str):
    recommendations = app.genre_based_recommendations(current_user.id, genre)

    return render_template('genre_search_results.html', recommendations=recommendations, length=len(recommendations),
                           genre=genre.replace('-', ' ').title())


@views.route("/ratings", methods=["GET", "POST"])
@login_required
def ratings():
    if request.method == "GET":
        user_ratings = []
        for rating in current_user.ratings:
            movie_info = app.data_manager.get_details_from_tmdbid(rating.tmdbId)
            user_ratings.append((movie_info, rating.rating))
        length = len(user_ratings)
        return render_template("my_ratings.html", ratings=user_ratings, length=length)
    else:

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

                ratings_df.reset_index(drop=True, inplace=True)
                flash("Rating Deleted Successfully", category="info")

        return redirect(request.form["redirect_url"])
