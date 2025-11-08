import pandas as pd

df = pd.read_csv("data.csv")
# print(df.head())

# Q1.

print("Total number of matches: ")
def_id = df["id"]
print(def_id.count())
# print(type(df.iloc[0]))
# print(df.index)

print("Columns: ")
print(df.columns)

print("First 5 rows of data: ")
print(df.head())

print("Describing data: ")
print(df.describe())
# print(df.info())


# Q2
# df2 = df["id", "win_by_runs", "win_by_wickets", "player_of_match"]
# print(df2)
print(df["player_of_match"].max())

# Q3
wkhd = df["venue":"Wankhede Stadium"]


# Q6
# c1 = df.columns("")