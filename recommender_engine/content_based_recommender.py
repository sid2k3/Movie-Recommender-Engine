from heapq import heapify, heappop
import sys

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:

    def __init__(self, meta_data, recommendations_needed):
        self.recommendations_needed = recommendations_needed
        cv = CountVectorizer()

        cosine_sim_matrix = cosine_similarity(cv.fit_transform(meta_data["tags"]))
        self.final_matrix = np.empty([len(cosine_sim_matrix), self.recommendations_needed, 2])
        print(f'SIZE:{sys.getsizeof(cosine_sim_matrix)}')

        self.filter_matrix(cosine_sim_matrix)
        print(f'SIZE1:{sys.getsizeof(self.final_matrix)}')
        # print(self.final_matrix.shape)

    def filter_matrix(self, cosine_sim_matrix):
        """Keeps only the top k(recommendations_needed) similar movies """

        for idx in range(len(cosine_sim_matrix)):
            print(f"{idx} of {range(len(cosine_sim_matrix))} movies ")

            similarity_scores = np.array([(-sim, int(idx1)) for idx1, sim in enumerate(cosine_sim_matrix[idx])])

            # After partitioning the 2d array, the first k(self.recommendations_needed)
            # indices would contain the k most similar movies

            partitioned_array = np.argpartition(similarity_scores[:, 0], self.recommendations_needed)

            # Removing extra movies and only keeping the k most similar movies
            most_similar_movies = similarity_scores[partitioned_array][:self.recommendations_needed]

            # Sorting the k most similar movies
            most_similar_movies = most_similar_movies[most_similar_movies[:, 0].argsort()]

            # Time complexity for each movie (partitioning and sorting) is O(n+klogk)

            self.final_matrix[idx] = most_similar_movies

    def recommend(self, idx):
        # print(self.final_matrix[idx].tolist())
        return self.final_matrix[idx].tolist()
