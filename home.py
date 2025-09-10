import streamlit as st
import pandas as pd

st.set_page_config(page_title="Most Popular Books", layout="wide")
st.title("📚 Most Popular Books")

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
agg = agg[agg["num_ratings"] >= 10]
agg["avg_rating"] = agg["avg_rating"].apply(lambda x: round(x / 2, 1) if x > 5 else round(x, 1))
most_popular = agg.sort_values(by="num_ratings", ascending=False).head(50)

# Display grid
cols_per_row = 5
rows = [most_popular.iloc[i:i+cols_per_row] for i in range(0, len(most_popular), cols_per_row)]

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
