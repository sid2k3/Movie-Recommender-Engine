# Additional Information about Movie Recommender System

## Table of Contents

1. [Project Structure and Working](#project-structure--working)
2. [Role of Algorithms](#role)

## Project Structure & Working

This project consists of two components.

* Recommender Engine
* Website

### Recommender Engine

The recommender engine is responsible for giving recommendations for a particular user or a movie. It is mainly divided
into four parts.

* Content Based Recommender
* Collaborative Filtering Based Recommender
* Data Processor
* Recommendations for user

#### Content Based Recommender

This class takes the metadata with tags (5000 most common keywords, top_cast, director, genre)
from the DataProcessor class as input and generates a matrix which stores the occurrence of each tag for each movie.
Every row of this matrix is a vector which tells us about the tags a particular movie contains. Similarity matrix is
then computing by calculating the [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) between each
movie vector and all other vectors.

Then each row of this matrix is partially sorted to include only the top k most similar movies for each movie. Whenever
recommendations are needed for a movie this recommender simply returns the data stored in the final resultant matrix for
that movie. This data includes the movie ids of the top k most similar movies along with their cosine similarity values
with the given movie.
<br>
<br>

![Content Based Recommender](https://i.imgur.com/5sE5hj9.png)

#### Collaborative Filtering Based Recommender

This class takes filtered user ratings from the DataProcessor class as input and generates a normalized user-rating
matrix. The filtered ratings are formed by combining the actual ratings from the database with the sample ratings (
cleaned_ratings.csv) from the dataset.

Each row of the generated matrix corresponds to a movie and each column corresponds to a user.

`Matrix[i][j] == Normalized Rating for Movie i given by User j`

Normalized rating is the actual rating given by a user subtracted by the mean rating of the same user.

This class then use
the [K Nearest Neighbours Algorithm (KNN)](https://scikit-learn.org/stable/modules/neighbors.html#neighbors) to find
similar movies for a given movie. The criteria used to find neighbours is
the [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) between the movie vectors (row of a matrix).
Since the matrix contains normalized ratings, we can say that we are using centered cosine similarity to compute similar
movies. Basically, this class implements item-item collaborative filtering using KNN. The model is retrained every 2
hours with the new data collected, this is done because the dataset used to train is quite small.
<br>
<br>
![Collaborative Filtering Based Recommender](https://i.imgur.com/JFgE7A7.png)

#### Data Processor

This class deals with all the data files. It is responsible for storing data from the csv files and the database in
dataframes. All the operations that are performed on the data are done in this class. It provides filtered data to both
the recommender classes. It contains utility functions to get, set and filter data. It also maintains a list of popular
movies and popular movies for each genre. Popular movies are those movies which have the highest weighted rating
according to IMDB's weighted rating formula. The popular movies are recomputed every day.

```
IMDB's Weighted Rating Formula
weighted rating (WR) = (v ÷ (v+m)) × R + (m ÷ (v+m)) × C where

         R = average for the movie (mean) = (Rating)
         v = number of votes for the movie = (votes)
         m = minimum votes required
         C = the mean vote across the whole dataset

```

#### Recommendations for user

Recommendations for a user are calculated by finding similar movies to all the positively
rated (`rating > avg user rating`) movies. Similar movies are computed by both the recommending techniques separately. A
score is given to each similar movie and only the top k movies with the highest scores are given to the website.

The formula to rank/score movies is -

```
Score of movie j if user has rated movie i

similarity_ij * normalized_user_rating

similarity_ij : similarity value given by the recommender. It represents how similar movie i is to movie j.  

normalized_user_rating : Actual rating given by user to movie i subtracted by the average rating of that particular user.
```  

If the user has rated no movies or the data is not enough to generate the minimum number of required recommendations,
then the recommendations are filled with popular movies.

___

### Website

The website is a standard Flask backend. It uses a [SQLite](https://www.sqlite.org/index.html) database to store user
information and user ratings.

#### Database Schema

<br>

![schema](https://i.imgur.com/62hqxvo.png)

___

## Role of Algorithms

Apart from the algorithms used to generate the recommendations there are a some other algorithms which play an integral
part in improving the performance of this application.

These algorithms include-

* Sorting
* Caching
* Searching
* Ranking

### Sorting

Since we are only interested in the top recommendations out of all the recommendations for a movie, sorting is required
at many places in this project. An efficient sorting algorithm is the key to faster performance.

In this project while computing the top k (16) content based recommendations for each movie, we are required to sort
each row of the similarity matrix which contains ≈8000 entries. Since we need only top k (16) entries from those 8000
entries for each row, a regular O(NlogN) sort would surely become a bottleneck in the whole computation process. As we
are dealing with numpy arrays here, it would be much better to use the functionality provided in the numpy library.

A better way to get top k recommendations is to first partition the array
using [numpy.ndarray.partition](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.partition.html#numpy.ndarray.partition)
which works in O(N) time. After partitioning the first k indices would contain the top k results. Now we can slice the
array and perform a normal [numpy.sort](https://numpy.org/doc/stable/reference/generated/numpy.sort.html) on the sliced
array. Since the sliced array is much smaller than the original array, this kind of sorting would result in a much
better average performance then a normal sort.  
<br>

> Note: We are not using heap sort because the matrix is a numpy.ndarray therefore a partial sort using the inbuilt functions is much easier to write and has performance similar to heap sort.

### Caching

In this project caching plays the most important role once the server has started. Since many users would need
recommendations for the same movie, it makes sense if we cache the results of some movies, this leads to a drastic
performance improvement.

In this project we are caching the results from the CollaborativeFilteringRecommender Class. These results are only
cached till the model is retrained.

To avoid using too much memory our cache has a max capacity to hold recommendations for ≈5% (400) movies.

#### Cache Replacement Policy

To ensure a higher hit ratio in this case, the cache
uses [LRU (Least Recently Used) Caching Algorithm](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU))
.

<br>

### Searching

Searching could improve the accuracy of the recommendations. It can become an implicit way of collecting data about the
user. The searches of the user can also be included while computing recommendations for the user. This would lead to
better recommendations without having an explicit dataset.  
<br>

### Ranking

Ranking recommendations is the most important task of a recommender. The formulae used to rank movies are already
discussed in the [first part ](#recommender-engine) of this document.
___