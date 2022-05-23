from website import create_app

app = create_app()  # Creating app first because next import is going to need the app database to work

from recommender_engine import cbr, data_manager, cfr, get_content_based_recommendations, get_recommendations_for_user, \
    get_hall_of_fame

app.cbr = cbr
app.data_manager = data_manager
app.cfr = cfr
app.hall_of_fame = get_hall_of_fame
app.cbr_recommender = get_content_based_recommendations
app.get_recommendations_for_user = get_recommendations_for_user

if __name__ == "__main__":
    app.run(debug=True)

# TODO REMOVE REQUESTS FROM REQUIREMENTS
