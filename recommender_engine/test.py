# from . import get_recommendations_for_user, cfr, data_manager

import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

root_dir = Path(__file__).parent

target_dir = root_dir.parent / "website"
cnx = create_engine(f'sqlite:///{target_dir}/database.db').connect()
df = pd.read_sql_table('Rating', cnx)
df = df[['userId', 'tmdbId', 'rating']]
df1 = pd.read_csv(root_dir / "cleaned_ratings.csv")

print(df1.head(5))
print(df.shape)
comb = pd.concat([df1, df], ignore_index=True)

print(comb.shape)
print(comb[comb["userId"] == 1])
