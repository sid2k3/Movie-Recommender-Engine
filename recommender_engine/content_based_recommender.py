from heapq import heapify, heappop
import sys
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:

    def __init__(self, meta_data, recommendations_needed):
        self.recommendations_needed = recommendations_needed
        cv = CountVectorizer()

        cosine_sim_matrix = cosine_similarity(cv.fit_transform(meta_data["tags"]))
        self.final_matrix = []
        print(f'SIZE:{sys.getsizeof(cosine_sim_matrix)}')

        self.filter_matrix(cosine_sim_matrix)
        print(f'SIZE:{sys.getsizeof(self.final_matrix)}')

    def filter_matrix(self, cosine_sim_matrix):
        """Keeps only the top k(recommendations_needed) similar movies """
        final_matrix = []

        for idx in range(len(cosine_sim_matrix)):
            print(f"{idx} of {range(len(cosine_sim_matrix))} movies ")
            similarity_scores = [(-sim, idx1) for idx1, sim in enumerate(cosine_sim_matrix[idx])]

            heapify(similarity_scores)
            # reducing complexity from nlogn to klogn
            most_similar_movie_indexes = [heappop(similarity_scores) for _ in
                                          range(self.recommendations_needed)]

            final_matrix.append(most_similar_movie_indexes)

        self.final_matrix = final_matrix

    def recommend(self, idx):
        return self.final_matrix[idx]
