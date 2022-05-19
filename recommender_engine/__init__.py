from .collaborative_filtering_based_recommender import CollaborativeFilteringRecommender
from .content_based_recommender import ContentBasedRecommender
from .data_processor import DataProcessor

NUMBER_OF_RECOMMENDATIONS = 12
data_manager = DataProcessor()
cbr = ContentBasedRecommender(data_manager.meta_data)
cfr = CollaborativeFilteringRecommender(data_manager.filtered_ratings(), NUMBER_OF_RECOMMENDATIONS)


# details = cfr.get_similar_movies_knn(24428)
#
# for id1, dis in details:
#     print(data_manager.get_title_from_tmdbid(id1))
def get_content_based_recommendations(tmdbid: int):
    """Returns similar movies based on content for a given movie."""
    print(tmdbid)
    idx = data_manager.get_index_from_tmdbid(tmdbid)

    similar_movie_indexes = [int(idx1) for sim_score, idx1 in cbr.recommend(idx)]
    return [data_manager.get_details_from_index(idx1) for idx1 in similar_movie_indexes]


def get_recommendations_for_user(user_id: int, mode: str):
    """Returns most related movies based on user rating history"""

    filter_movies = True

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
            print(related_movies)
            for similarity, movie_idx in related_movies:
                score = (-similarity) * normalized_user_rating
                similar_movie_tmdbid = data_manager.get_tmdbid_from_index(movie_idx)
                movie_scores.append((similar_movie_tmdbid, score))

    movie_scores = sorted(movie_scores, key=lambda x: x[1], reverse=True)
    # TODO heap sort here
    unique_movies = []
    visited = set()

    # Removing duplicate recommendations
    for movie_id, score in movie_scores:
        if movie_id not in visited:
            unique_movies.append(movie_id)
            visited.add(movie_id)

    if len(unique_movies) < NUMBER_OF_RECOMMENDATIONS:
        extra_recommendations = NUMBER_OF_RECOMMENDATIONS - len(unique_movies)
        unique_movies.extend(data_manager.get_most_popular_movies()[:extra_recommendations])
        # If we are getting less recommendations than the required number due to lack of data
        # most popular movies are added to get the required number of recommendations

    for movie_id in unique_movies:
        print(data_manager.get_title_from_tmdbid(movie_id))

    return [data_manager.get_title_from_tmdbid(movie_id) for movie_id in unique_movies]


get_recommendations_for_user(1, "cbr")
#
# get_recommendations_for_user(100001, "cfr")

# for tmdbid in data_manager.get_most_popular_movies():
#     print(data_manager.get_title_from_tmdbid(tmdbid))

# TODO use set for recommendations instead of list
# TODO include content based recommendations based on history of user
# TODO add high rated movies if amount of similar movies are less
# TODO change k value to 12
# TODO include movies if rated above mean
