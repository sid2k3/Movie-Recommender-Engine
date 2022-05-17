from website import create_app
from recommender_engine import cbr, data_manager, cfr, get_content_based_recommendations

app = create_app()
app.cbr = cbr
app.data_manager = data_manager
app.cfr = cfr
app.cbr_recommender = get_content_based_recommendations

if __name__ == "__main__":
    app.run(debug=True)
