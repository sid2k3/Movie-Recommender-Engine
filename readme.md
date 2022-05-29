# Movie Recommender System

This project was built as a part of [Microsoft Engage 2022](https://acehacker.com/microsoft/engage2022/).

## Table of Contents

1. [About The Project](#about-the-project)
2. [Features Implemented](#features-implemented)
3. [Project Timeline](#project-timeline)
4. [Built With](#built-with)
5. [Instructions To Run](#instructions-to-run)
6. [Video Demonstration](#demonstration-video)

### About The Project

A movie recommender web application, which gives personalized recommendations to users based on their rating history.

Users can also find recommendations by genre or by searching for a particular movie.

##### Features Implemented

1. Content Based Recommendations
2. Collaborative Filtering Based Recommendations
3. Recommendations using IMDB's weighted rating formula
4. Search
5. Recommendations by Genre

### Project Timeline

This project was built in 4 phases. Total time taken to complete this project was ≈ 3 weeks.
<br>
<br>
![Project Timeline](https://i.imgur.com/Fjxz8TC.png)

### Built With

* Flask
* Pandas / Numpy
* Scikit-learn
* Bootstrap
* Select2
* SQLite

### Instructions To Run

There are two ways to run this application. The simplest one is to use Docker.

#### 1. Docker Installation

1. Install Docker for your system
2. Run the following command

```
docker run -p 5000:5000 sid2k3/movie_recommender:latest
```

#### 2. Manual Installation

1. Install python 3.9
2. Clone this repository
3. Run the following command

```
python -m venv <venv_name>
```

4. Activate the virtual environment

In CMD / Windows

```
<venv_name>\Scripts\activate.bat
```

In Bash / Linux

```
source <venv_name>/bin/activate
```

5. Install the dependencies

```
pip install -r requirements.txt
```

6. Start the server

```
python main.py
```

> Note: The recommender requires around 1 minute of one time precomputation. Please wait
> while it completes this step.

### Demonstration Video

To view the video click [here]().