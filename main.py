from website import create_app
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = create_app()  # Creating app first because next import is going to need the app database to work

from recommender_engine import data_manager, \
    get_content_based_recommendations, get_recommendations_for_user, \
    get_hall_of_fame, retrain_model, recompute_popular_movies, get_recommendations_based_on_genre

app.data_manager = data_manager

app.hall_of_fame = get_hall_of_fame
app.cbr_recommender = get_content_based_recommendations
app.get_recommendations_for_user = get_recommendations_for_user
app.genre_based_recommendations = get_recommendations_based_on_genre
scheduler = BackgroundScheduler()

scheduler.add_job(func=retrain_model, trigger="interval", hours=2)
scheduler.add_job(func=recompute_popular_movies, trigger="interval", hours=24)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
