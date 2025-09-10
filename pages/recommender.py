import pickle
import streamlit as st
import numpy as np
import pandas as pd
import requests

st.title("📚 Book Recommender using Machine Learning")

# Load data
model = pickle.load(open('model.pkl', 'rb'))
books_name = pickle.load(open('book_names.pkl', 'rb'))
final_rating = pickle.load(open('final_rating.pkl', 'rb'))
book_pivot = pickle.load(open('book_pivot.pkl', 'rb'))

books_csv = pd.read_csv("BX-Books.csv", sep=";", on_bad_lines="skip", encoding="latin-1")
ratings_csv = pd.read_csv("BX-Book-Ratings.csv", sep=";", on_bad_lines="skip", encoding="latin-1")
merged_ratings = ratings_csv.merge(books_csv, on="ISBN")

# Helpers
def get_image_column(df):
    for col in ['img_url', 'Image-URL-L', 'Image-URL-M', 'image_url', 'ImageURL']:
        if col in df.columns:
            return col
    return None

IMAGE_COL = get_image_column(final_rating)

def format_rating(value):
    if value is None or pd.isna(value):
        return "⭐ Rating: N/A"
    try:
        v = float(value)
        v = round(v / 2, 1) if v > 5 else round(v, 1)
        return f"⭐ {v}/5"
    except:
        return "⭐ Rating: N/A"

api_cache = {}
def fetch_description_from_google(title):
    if title in api_cache:
        return api_cache[title]
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{requests.utils.quote(title)}"
        r = requests.get(url, timeout=6)
        data = r.json()
        if "items" in data and data["items"]:
            vi = data["items"][0].get("volumeInfo", {})
            description = vi.get("description", "No description available.")
            api_cache[title] = description
            return description
    except:
        pass
    api_cache[title] = "No description available."
    return api_cache[title]

def fetch_book_details(suggestion_indices):
    details = []
    for idx in suggestion_indices:
        title = book_pivot.index[idx]
        match = final_rating.loc[final_rating['title'] == title]
        img_url = None
        description = None
        isbn = None

        if not match.empty:
            row = match.iloc[0]
            if IMAGE_COL and pd.notna(row.get(IMAGE_COL)):
                img_url = row[IMAGE_COL]
            if 'isbn' in row and pd.notna(row['isbn']):
                isbn = row['isbn']
            if 'description' in row and pd.notna(row['description']):
                description = row['description']

        book_ratings = merged_ratings.loc[merged_ratings['Book-Title'] == title]
        if not book_ratings.empty:
            avg_rating = book_ratings['Book-Rating'].mean()
            rating_str = format_rating(avg_rating)
        else:
            rating_str = "⭐ Rating: N/A"

        if not description:
            description = fetch_description_from_google(title)
        if not img_url:
            img_url = "https://via.placeholder.com/150?text=No+Image"
        if not isbn:
            isbn = "ISBN: N/A"

        details.append({
            "title": title,
            "image": img_url,
            "description": description,
            "rating": rating_str,
            "isbn": isbn
        })
    return details

def recommend_books(selected_title):
    try:
        book_id = np.where(book_pivot.index == selected_title)[0][0]
    except IndexError:
        return []
    _, suggestion = model.kneighbors(
        book_pivot.iloc[book_id, :].values.reshape(1, -1),
        n_neighbors=6
    )
    suggestion = suggestion.flatten().tolist()
    suggestion = [i for i in suggestion if book_pivot.index[i] != selected_title]
    return fetch_book_details(suggestion)

# UI
selected_books = st.selectbox("Type or select a book from the dropdown", books_name)

if st.button("Show Recommendation"):
    recommendations = recommend_books(selected_books)
    if not recommendations:
        st.info("No recommendations found for this title.")
    else:
        cols = st.columns(len(recommendations))
        for i, col in enumerate(cols):
            col.image(recommendations[i]["image"])
            col.markdown(f"**{recommendations[i]['title']}**")
            col.caption(recommendations[i]["rating"])
            col.markdown(f"[ISBN: {recommendations[i]['isbn']}](https://www.google.com/search?q=isbn+{recommendations[i]['isbn']})")
            col.write(recommendations[i]["description"])
