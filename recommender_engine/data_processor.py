from ast import literal_eval
from collections import Counter
from pathlib import Path
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
from sqlalchemy import create_engine
from pathlib import Path

root_dir = Path(__file__).parent

target_dir = root_dir.parent / "website"
cnx = create_engine(f'sqlite:///{target_dir}/database.db').connect()

GENRE_BASED_RECOMMENDATIONS = 24  # Number of recommendations shown for each genre


# print(root_dir)


class DataProcessor:

    def __init__(self):
        self.popular_movies = []  # Stores the top 15 highest rated movies according to IMDB's formula

        self.original_metadata = pd.read_csv(root_dir / "cleaned_data.csv")
        print(self.original_metadata.head(5))
        print(self.original_metadata.shape)
        self.meta_data = pd.read_csv(root_dir / "cleaned_data.csv")

        self.sample_ratings = pd.read_csv(root_dir / "cleaned_ratings.csv")

        self.actual_ratings = pd.read_sql_table('Rating', cnx)
        self.actual_ratings = self.actual_ratings[['userId', 'tmdbId', 'rating']]

        print(self.actual_ratings)
        self.combined_ratings = pd.concat([self.sample_ratings, self.actual_ratings], ignore_index=True)

        self.create_tags()

        self.genre_to_id = {'action': 0, 'adventure': 1, 'comedy': 2,
                            'romance': 3, 'science-fiction': 4, 'thriller': 5}

        self.popular_movies_by_genre = [[], [], [], [], [], []]

        self.popular_movies = []
        self.compute_popular_movies()

    def filtered_ratings(self):
        # TODO USE COMBINED DF HERE

        # Recalculating combined ratings before providing data to CFR class
        self.combined_ratings = pd.concat([self.sample_ratings, self.actual_ratings], ignore_index=True)
        # print(self.combined_ratings[self.combined_ratings["userId"] == 1])

        user_ratings = self.filter_users(self.combined_ratings)
        user_ratings = self.filter_movies(user_ratings)
        print(user_ratings[user_ratings["userId"] == 1])
        return user_ratings

    def create_tags(self):
        self.format_data_for_tags()
        self.stem_keywords()
        self.remove_rare_keywords()

        self.meta_data["tags"] = self.meta_data["keywords"] + self.meta_data["top_cast"] + self.meta_data[
            "director"] + self.meta_data["genres"]

        self.meta_data["tags"] = self.meta_data["tags"].apply(lambda tags_list: " ".join(tags_list))

    def format_data_for_tags(self):
        self.meta_data['keywords'] = self.meta_data['keywords'].apply(literal_eval)
        self.meta_data["top_cast"] = self.meta_data["top_cast"].apply(literal_eval)
        self.meta_data["genres"] = self.meta_data["genres"].apply(literal_eval)

        self.meta_data['top_cast'] = self.meta_data['top_cast'].apply(
            lambda x: [str.lower(i.replace(" ", "")) for i in x])
        self.meta_data['director'] = self.meta_data['director'].astype('str').apply(
            lambda x: str.lower(x.replace(" ", "")))

        self.meta_data['director'] = self.meta_data['director'].apply(lambda x: [x, x])
        # increasing weight of director by mentioning director twice

    def stem_keywords(self):
        stemmer = SnowballStemmer('english')
        self.meta_data['keywords'] = self.meta_data['keywords'].apply(
            lambda keyword_list: [stemmer.stem(word) for word in keyword_list])

    # def is_common_keyword(keyword_list: list):
    #     return [word for word in keyword_list if word in common_keywords]

    def remove_rare_keywords(self):
        coun = Counter()
        for idx, keyword_list in self.meta_data["keywords"].items():
            coun.update(keyword_list)

        # Consider keyword if keyword in 5000 most common keywords

        common_keywords = set([word for word, freq in coun.most_common(5000)])

        # print(common_keywords)

        self.meta_data["keywords"] = self.meta_data["keywords"].apply(lambda keyword_list1:
                                                                      [word for word in keyword_list1 if
                                                                       word in common_keywords])

        # converting keywords to lowercase and removing spaces from keywords
        self.meta_data['keywords'] = self.meta_data['keywords'].apply(
            lambda keyword_list1: [str.lower(keyword.replace(" ", "")) for keyword in keyword_list1])

    def filter_movies(self, ratings_df):
        """Removes movies which have less than minimum (10) ratings"""

        min_ratings = 10  # min ratings required to be considered in data analysis
        # TODO USE COMBINED DF HERE
        movies_with_total_rating_counts = self.combined_ratings["tmdbId"].value_counts()

        movies_to_be_included = movies_with_total_rating_counts.gt(
            min_ratings)  # dataframe where index is tmdbId and value is True or False

        # movies_to_be_included[movies_to_be_included] is a dataframe
        # where index represents all movies which are to be included

        ratings_df = ratings_df.loc[ratings_df["tmdbId"].isin(movies_to_be_included[movies_to_be_included].index)]

        return ratings_df

    def filter_users(self, ratings_df):
        """Removes users which have rated less than min number of movies required (10)"""

        min_number_of_movies_rated = 10  # min movies that need to be rated by the user

        users_with_total_rating_counts = ratings_df["userId"].value_counts()

        users_to_be_included = users_with_total_rating_counts.gt(
            min_number_of_movies_rated)  # dataframe where index is userId and value is True or False

        # users_to_be_included[users_to_be_included] is a dataframe
        # in which index represents all the users to be included

        ratings_df = ratings_df.loc[ratings_df["userId"].isin(users_to_be_included[users_to_be_included].index)]

        return ratings_df

    def get_positively_rated_movies(self, user_id: int, filter_on: bool):
        """Returns the most positively rated movies by the user.
        Movies that are rated below the avg user rating for a specific user are removed."""

        # TODO READ FROM ACTUAL DF HERE
        all_movies_rated_by_user = self.actual_ratings[self.actual_ratings["userId"] == user_id]

        if filter_on:
            all_movies_rated_by_user = self.filter_movies(all_movies_rated_by_user)

        avg_user_rating = all_movies_rated_by_user["rating"].mean()

        positively_rated_movies = all_movies_rated_by_user[
            all_movies_rated_by_user["rating"] > avg_user_rating]
        # removes movies with rating less than equal to mean user rating

        positively_rated_movies["rating"] = positively_rated_movies["rating"].sub(avg_user_rating)
        print(positively_rated_movies)
        return positively_rated_movies

    def compute_popular_movies(self):
        """Updates the N (32) most positively rated movies using IMDB's weighted rating formula.
        Also computes the 24 most popular movies for each genre.
        """

        # TODO USE COMBINED DF HERE
        popular_movies = []
        self.popular_movies_by_genre = [[], [], [], [], [], []]

        df = self.combined_ratings.groupby("tmdbId")
        avg_ratings = df.mean()["rating"]
        vote_counts = df.count()["rating"]

        # weighted rating (WR) = (v ÷ (v+m)) × R + (m ÷ (v+m)) × C where:

        # R = average for the movie (mean) = (Rating)
        # v = number of votes for the movie = (votes)
        # m = minimum votes required
        # C = the mean vote across the whole dataset

        overall_mean = avg_ratings.mean()

        for tmdbid in self.combined_ratings["tmdbId"].unique():
            num_of_votes = vote_counts[tmdbid]
            min_votes_required = 100

            avg_rating_for_given_movie = avg_ratings[tmdbid]

            weighted_rating = (num_of_votes / (num_of_votes + min_votes_required)) * avg_rating_for_given_movie
            weighted_rating += (min_votes_required / (num_of_votes + min_votes_required)) * overall_mean
            popular_movies.append((weighted_rating, tmdbid))

        popular_movies = sorted(popular_movies, reverse=True)

        for rating, tmdbId in popular_movies:
            genres = self.get_genres_for_movie(tmdbId)

            for genre in genres:
                genre = genre.lower().replace(' ', '-')
                if genre == 'action':
                    genre_id = self.genre_to_id[genre]
                    if len(self.popular_movies_by_genre[genre_id]) < GENRE_BASED_RECOMMENDATIONS:
                        self.popular_movies_by_genre[genre_id].append(tmdbId)

                if genre == 'adventure':
                    genre_id = self.genre_to_id[genre]
                    if len(self.popular_movies_by_genre[genre_id]) < GENRE_BASED_RECOMMENDATIONS:
                        self.popular_movies_by_genre[genre_id].append(tmdbId)

                if genre == 'comedy':
                    genre_id = self.genre_to_id[genre]
                    if len(self.popular_movies_by_genre[genre_id]) < GENRE_BASED_RECOMMENDATIONS:
                        self.popular_movies_by_genre[genre_id].append(tmdbId)

                if genre == 'romance':
                    genre_id = self.genre_to_id[genre]
                    if len(self.popular_movies_by_genre[genre_id]) < GENRE_BASED_RECOMMENDATIONS:
                        self.popular_movies_by_genre[genre_id].append(tmdbId)

                if genre == 'science-fiction':
                    genre_id = self.genre_to_id[genre]
                    if len(self.popular_movies_by_genre[genre_id]) < GENRE_BASED_RECOMMENDATIONS:
                        self.popular_movies_by_genre[genre_id].append(tmdbId)

                if genre == 'thriller':
                    genre_id = self.genre_to_id[genre]
                    if len(self.popular_movies_by_genre[genre_id]) < GENRE_BASED_RECOMMENDATIONS:
                        self.popular_movies_by_genre[genre_id].append(tmdbId)

                total_len = sum([len(lst) for lst in self.popular_movies_by_genre])

                if total_len == GENRE_BASED_RECOMMENDATIONS * len(
                        self.popular_movies_by_genre):  # movies for all genres are computed
                    break

        popular_movies = popular_movies[:32]
        self.popular_movies = popular_movies

    def get_genres_for_movie(self, tmdbid):
        print("************************")
        print(self.original_metadata[self.original_metadata['tmdbId'] == tmdbid]['genres'].item())
        return literal_eval(self.original_metadata[self.original_metadata['tmdbId'] == tmdbid]['genres'].item())

    def get_most_popular_movies(self):
        return [movie_id for weighted_rating, movie_id in self.popular_movies]

    def get_title_from_tmdbid(self, tmdbid):
        return self.original_metadata[self.original_metadata["tmdbId"] == tmdbid]["title"].to_list()[0]

    def get_index_from_tmdbid(self, tmdbid):
        """Returns absolute index of movie with given tmdbid from original metadata"""
        return self.original_metadata.index[self.original_metadata['tmdbId'] == tmdbid].tolist()[0]

    def get_tmdbid_from_index(self, idx):
        return self.original_metadata.iloc[idx]["tmdbId"]

    def get_details_from_index(self, idx):
        return self.get_details_from_tmdbid(self.get_tmdbid_from_index(idx))

    def get_details_from_tmdbid(self, tmdbid):
        df = self.original_metadata[self.original_metadata["tmdbId"] == tmdbid]
        df = df[["title", "tmdbId", "poster_url"]]

        # print(df.to_dict("records"))
        return df.to_dict("records")[0]

    def get_all_movies(self):
        df = self.original_metadata[["title", "tmdbId"]]
        df = df.to_dict("records")
        return df

    # TODO CREATE ACTUAL RATINGS DF
