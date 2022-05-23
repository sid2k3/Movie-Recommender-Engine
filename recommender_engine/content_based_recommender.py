from functools import lru_cache
from heapq import heapify, heappop

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:

    def __init__(self, meta_data, recommendations_needed):
        self.recommendations_needed = recommendations_needed
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(meta_data["tags"])

        self.cosine_sim_matrix = cosine_similarity(count_matrix)

    @lru_cache(900)  # caching 10% of total movies
    def recommend(self, idx):
        # title = (title.replace(" ", "").lower())
        # idx = indices[title]
        similarity_scores = [(-sim, idx1) for idx1, sim in enumerate(self.cosine_sim_matrix[idx])]
        # print(similarity_scores)
        heapify(similarity_scores)

        most_similar_movie_indexes = [heappop(similarity_scores) for _ in
                                      range(self.recommendations_needed)]  # reducing complexity from nlogn to klogn

        print(most_similar_movie_indexes)
        # returns [(-similarity,movie_index)]
        return most_similar_movie_indexes
