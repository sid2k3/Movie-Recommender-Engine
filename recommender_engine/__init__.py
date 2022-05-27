from .collaborative_filtering_based_recommender import CollaborativeFilteringRecommender
from .content_based_recommender import ContentBasedRecommender
from .data_processor import DataProcessor

NUMBER_OF_RECOMMENDATIONS = 16  # Recommendations needed from each recommender algorithm

NUMBER_OF_FILTERED_RECOMMENDATIONS = 12
# Final number of recommendations
# given to the website (after eliminating common recommendations)

GENRE_BASED_RECOMMENDATIONS = 24  # Number of recommendations shown for each genre

data_manager = DataProcessor()
cbr = ContentBasedRecommender(data_manager.meta_data, NUMBER_OF_RECOMMENDATIONS)

cfr = CollaborativeFilteringRecommender(data_manager.filtered_ratings(), NUMBER_OF_RECOMMENDATIONS)


def retrain_model():
    """Runs the knn algo every hour and updates matrix with new data."""
    global cfr

    print("Retraining Model")

    new_cfr = CollaborativeFilteringRecommender(data_manager.filtered_ratings(), NUMBER_OF_RECOMMENDATIONS)
    cfr = new_cfr


def recompute_popular_movies():
    """Runs once a day to calculate popular movies of the day."""
    print("Recomputing Popular Movies")

    data_manager.compute_popular_movies()


def get_content_based_recommendations(tmdbid: int):
    """Returns similar movies based on content for a given movie."""

    idx = data_manager.get_index_from_tmdbid(tmdbid)

    similar_movie_indexes = [int(idx1) for sim_score, idx1 in
                             cbr.recommend(idx)[:NUMBER_OF_FILTERED_RECOMMENDATIONS]]
    return [data_manager.get_details_from_index(idx1) for idx1 in similar_movie_indexes]


def get_separate_recommendations(user_id: int, mode: str):
    """Returns most related movies based on user rating history and on the mode
    of recommendation selected (cbr or cfr)."""

    filter_movies = True  # Filters out movies which have very few ratings(currently 10).

    if mode == "cbr":
        filter_movies = False
    # We don't need to filter movies based on ratings if we are using content based recommender

    positively_rated_movies = data_manager.get_positively_rated_movies(user_id, filter_movies)

    movie_scores = []

    for idx, row in positively_rated_movies.iterrows():
        movie_tmdbid = row["tmdbId"]
        normalized_user_rating = row["rating"]
        if mode == "cfr":
            related_movies = cfr.get_similar_movies_knn(movie_tmdbid)
            related_movies = related_movies[1:]  # removing the movie that user has already rated/watched

            for movie_id, distance in related_movies:

                if distance != 0:
                    score = (1 / distance) * normalized_user_rating  # 1/distance is closeness
                else:
                    score = 1000000000000 * normalized_user_rating

                # To handle division by 0 if distance is 0
                movie_scores.append((movie_id, score))

        elif mode == "cbr":

            movie_idx = data_manager.get_index_from_tmdbid(movie_tmdbid)
            related_movies = cbr.recommend(movie_idx)
            related_movies = related_movies[1:]  # removing the movie that user has already rated/watched

            for similarity, movie_idx in related_movies:
                score = (-similarity) * normalized_user_rating
                similar_movie_tmdbid = data_manager.get_tmdbid_from_index(int(movie_idx))
                movie_scores.append((similar_movie_tmdbid, score))

    movie_scores = sorted(movie_scores, key=lambda x: x[1], reverse=True)

    unique_movies = []
    visited = set()

    # Removing duplicate recommendations
    for movie_id, score in movie_scores:
        if movie_id not in visited:
            unique_movies.append(movie_id)
            visited.add(movie_id)

    if len(unique_movies) < NUMBER_OF_RECOMMENDATIONS:
        fill_recommendations(unique_movies, NUMBER_OF_RECOMMENDATIONS)
        # If we are getting less recommendations than the required number due to lack of data
        # most popular movies are added to get the required number of recommendations
    else:
        unique_movies = unique_movies[:NUMBER_OF_RECOMMENDATIONS]

    return unique_movies
    # returns list of tmdbIds


def fill_recommendations(current_movie_list: list, recommendations_needed):
    """Fills the recommendations with popular
    movies if we don't get the required no. of recommendations"""
    extra_recommendations = recommendations_needed - len(current_movie_list)
    current_movie_list.extend(data_manager.get_most_popular_movies()[:extra_recommendations])


def get_hall_of_fame():
    """Returns details of the top 3 popular movies"""
    hall_of_fame = data_manager.get_most_popular_movies()[:3]
    return [data_manager.get_details_from_tmdbid(movie_id) for movie_id in hall_of_fame]


def get_recommendations_for_user(user_id: int) -> dict:
    """Gets recommendations from both algorithms and eliminates
    common recommendations."""

    cbr_recommendations = get_separate_recommendations(user_id, 'cbr')
    cfr_recommendations = get_separate_recommendations(user_id, 'cfr')

    set1 = set(cbr_recommendations)

    filtered_cbr_recommendations = cbr_recommendations
    filtered_cfr_recommendations = []

    popular_movies = data_manager.get_most_popular_movies()

    for movie in cfr_recommendations:
        if movie not in set1:
            filtered_cfr_recommendations.append(movie)

    extra_recommendations_needed = NUMBER_OF_FILTERED_RECOMMENDATIONS - len(filtered_cfr_recommendations)

    for movie in popular_movies:
        if extra_recommendations_needed <= 0:
            break

        if movie not in set1:
            filtered_cfr_recommendations.append(movie)
            extra_recommendations_needed -= 1

    filtered_cfr_recommendations = filtered_cfr_recommendations[:NUMBER_OF_FILTERED_RECOMMENDATIONS]
    filtered_cbr_recommendations = filtered_cbr_recommendations[:NUMBER_OF_FILTERED_RECOMMENDATIONS]

    filtered_cbr_recommendations = [data_manager.get_details_from_tmdbid(movie_id) for movie_id in
                                    filtered_cbr_recommendations]
    # Replace movie ids with movie details
    filtered_cfr_recommendations = [data_manager.get_details_from_tmdbid(movie_id) for movie_id in
                                    filtered_cfr_recommendations]

    return {'cbr': filtered_cbr_recommendations, 'cfr': filtered_cfr_recommendations}


def get_recommendations_based_on_genre(user_id: int, genre_needed: str):
    """Returns only those movies which belong to the given genre.
    Movies are taken from user recommendations (cfr and cbr) and popular movies."""

    all_recommendations = get_recommendations_for_user(user_id)

    genre_based_recommendations = []
    genre_id_needed = data_manager.genre_to_id[genre_needed]

    for rec_type in all_recommendations.values():

        for movie in rec_type:

            genres = data_manager.get_genres_for_movie(movie['tmdbId'])
            for genre in genres:
                genre = genre.lower().replace(' ', '-')
                try:
                    genre_id = data_manager.genre_to_id[genre]

                    if genre_id == genre_id_needed:  # movie belongs to the genre
                        genre_based_recommendations.append(movie['tmdbId'])
                        break
                except KeyError:  # some other genre
                    continue

    # filling recommendations with popular movies of same genre

    genre_based_recommendations.extend(data_manager.popular_movies_by_genre[genre_id_needed])

    # eliminating common recommendations
    genre_based_recommendations = list(set(genre_based_recommendations))
    genre_based_recommendations = [data_manager.get_details_from_tmdbid(movie_id) for movie_id in
                                   genre_based_recommendations]
    return genre_based_recommendations[:GENRE_BASED_RECOMMENDATIONS]
