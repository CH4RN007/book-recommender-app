import streamlit as st
import pandas as pd

st.title("🏆 Top Rated Books")

# Load CSVs
books = pd.read_csv("BX-Books.csv", sep=";", on_bad_lines="skip", encoding="latin-1")
ratings = pd.read_csv("BX-Book-Ratings.csv", sep=";", on_bad_lines="skip", encoding="latin-1")

# Merge and aggregate
merged = ratings.merge(books, on="ISBN")
agg = merged.groupby(
    ["ISBN", "Book-Title", "Book-Author", "Image-URL-M"], as_index=False
).agg(
    avg_rating=("Book-Rating", "mean"),
    num_ratings=("Book-Rating", "count")
)

# Filter and sort
min_votes = st.slider("Minimum number of ratings", 5, 100, 10)
agg = agg[agg["num_ratings"] >= min_votes]
agg["avg_rating"] = agg["avg_rating"].apply(lambda x: round(x / 2, 1) if x > 5 else round(x, 1))
top_rated = agg.sort_values(by="avg_rating", ascending=False).head(50)

# Display grid
cols_per_row = 5
rows = [top_rated.iloc[i:i+cols_per_row] for i in range(0, len(top_rated), cols_per_row)]

for row in rows:
    cols = st.columns(cols_per_row)
    for col, (_, book) in zip(cols, row.iterrows()):
        with col:
            st.image(book["Image-URL-M"], width=120)
            st.markdown(f"**{book['Book-Title']}**")
            st.caption(f"by {book['Book-Author']}")
            st.write(f"⭐ {book['avg_rating']}/5")
            st.write(f"Ratings: {book['num_ratings']}")
            st.markdown(f"[ISBN: {book['ISBN']}](https://www.google.com/search?q=isbn+{book['ISBN']})")
