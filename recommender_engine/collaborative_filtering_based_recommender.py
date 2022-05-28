from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from functools import lru_cache


class CollaborativeFilteringRecommender:

    def __init__(self, user_ratings, neighbors_needed):
        # user_ratings is ratings after applying all filters

        self.user_rating_matrix = generate_normalized_matrix(user_ratings)

        self.movie_ids_to_indices = {}
        # maps movie ids to indices in sparse matrix
        idx = 0
        for movie_id in self.user_rating_matrix.index:
            self.movie_ids_to_indices[movie_id] = idx
            idx += 1

        self.indices_to_movie_ids = {v: k
                                     for k, v in self.movie_ids_to_indices.items()}

        # maps indices of sparse matrix to movie_ids

        self.neighbors_needed = neighbors_needed
        self.user_rating_matrix = csr_matrix(
            self.user_rating_matrix.values)
        # using csr_matrix to save space since matrix is sparse

        self.knn_model = NearestNeighbors(n_neighbors=neighbors_needed, metric='cosine', algorithm='auto')
        self.knn_model.fit(self.user_rating_matrix)

    @lru_cache(400)  # caching results for 5% of the movies
    def get_similar_movies_knn(self, movie_tmdbid):
        """Returns the details (tmdbid,distance) of the most related movies to the given
        movie using collaborative filtering model. Distance is inversely proportional to closeness of the movie."""

        try:

            movie_vector = self.user_rating_matrix.getrow(self.movie_ids_to_indices[movie_tmdbid]).toarray()
            distances, indices = self.knn_model.kneighbors(movie_vector,
                                                           n_neighbors=self.neighbors_needed)
            distances = distances.flatten()
            indices = indices.flatten()
            similar_movie_ids = []
            for list_idx, movie_idx in enumerate(indices):
                tmdbid = self.indices_to_movie_ids[
                    movie_idx]  # get tmdb id from absolute index (idx) of sparse matrix
                similar_movie_ids.append((tmdbid, distances[list_idx]))

            return [(movie_tmdbid, distance) for movie_tmdbid, distance in
                    sorted(similar_movie_ids, key=lambda x: x[1])]

        except KeyError:
            print("Movie doesn't exist in user_rating matrix")
            # If the movie got filtered due to less user ratings
            # or model is using old data the movie wouldn't exist in the user rating matrix
            return []


def generate_normalized_matrix(user_ratings):
    """Subtracts each user's rating by the mean of that user's rating.
    This is done to handle generous raters as well as non generous raters."""

    user_rating_matrix = user_ratings.pivot_table(index='tmdbId', columns='userId', values='rating')

    user_rating_matrix = user_rating_matrix.subtract(user_rating_matrix.mean(axis=0),
                                                     axis=1)
    # subtracting column mean from each column element to normalize each user's rating

    user_rating_matrix.fillna(0, inplace=True)
    return user_rating_matrix
