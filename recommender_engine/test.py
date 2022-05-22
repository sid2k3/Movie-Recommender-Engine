# from . import get_recommendations_for_user, cfr, data_manager
import requests

import pandas as pd

from sqlalchemy import create_engine
from pathlib import Path

#
root_dir = Path(__file__).parent
#
target_dir = root_dir.parent / "website"
cnx = create_engine(f'sqlite:///{target_dir}/database.db').connect()
df = pd.read_sql_table('Rating', cnx)
df = df[['userId', 'tmdbId', 'rating']]
# df1 = pd.read_csv(root_dir / "cleaned_ratings.csv")
#
# print(df1.head(5))
# print(df.shape)
# comb = pd.concat([df1, df], ignore_index=True)
#
# print(comb.shape)
# print(comb[comb["userId"] == 1])
#
# df = pd.read_csv(root_dir.parent / "cleaned_data3.csv")
# print(df.shape)
# df = df[["title", "tmdbId", "genres", "keywords", "poster_url", "top_cast", "director"]]
# df = df[df["genres"] != "[]"]
# print(df.shape)
#
# df.to_csv(root_dir.parent / "cleaned_data4.csv")
print(df.head(15))
df.drop(df.loc[
            (df['userId'] == 1) & (
                    df['tmdbId'] == 863)].index, inplace=True)

print(df.head(15))
