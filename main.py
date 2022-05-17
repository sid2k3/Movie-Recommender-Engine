from website import create_app
from recommender_engine import cbr, data_manager, cfr

app = create_app()
app.cbr = cbr
app.data_manager = data_manager
app.cfr = cfr

if __name__ == "__main__":
    app.run(debug=True)
