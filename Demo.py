import pandas as pd

PARQUET_PATH = "data/documents.parquet"

df = pd.read_parquet(PARQUET_PATH)

print(df.info())

#New
print("===")

print(df["IssueDate"].head())
print(df["IssueDate"].dt.year.head())
print(df["IssueDate"].dt.month.head())
print(df["IssueDate"].dt.day.head())

#New
print("===")

print(
    df["IssueDate"]
    .dt.year
    .value_counts()
    .sort_index()
)


#New
print("===")

print(
    df["IssueDate"]
    .dt.month
    .value_counts()
    .sort_index()
)


#New
print("===")

acoat = df["Acoat"].astype("string")

bad = df[acoat.str.len() != 5]

print("Invalid Acoat rows:", len(bad))

acoat = df["Acoat"].astype("string")

print(
    acoat[
        ~acoat.str.match(r"^[0-9A-Z]{5}$")
    ].unique()
)

#New
print("===")

for col in [
    "Acoat",
    "GRACO",
    "Supplier",
    "Region"
]:
    print(
        f"{col}: "
        f"{df[col].nunique():,} unique values"
    )

#New
print("===")

print(df["IssueDate"].min())
print(df["IssueDate"].max())

#New
print("===")


print(
    df["Supplier"]
    .value_counts()
    .head(20)
)

#New
print("===")

print(
    df["Lang"]
    .value_counts()
)


print("===")
print("=WOW=")

print(
    df.groupby(
        [
            df["IssueDate"].dt.year,
            "Supplier"
        ]
    )
    .size()
    .sort_values(ascending=False)
    .head(20)
)
