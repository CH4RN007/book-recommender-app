Book Recommendation App

1. Project Overview
This Streamlit app is a multi‑page book discovery platform built on:
- Home.py → Most Popular Books (by number of ratings)
- pages/TopRated.py → Top Rated Books (by average rating)
- pages/Recommender.py → ML‑based book recommendations with descriptions

All pages now:
- Show cover image, title, author, rating (/5), number of ratings (where applicable), and ISBN.
- ISBN is clickable → opens a normal Google search in the format `isbn <number>` in the “All” tab.

2. Data Sources
- BX-Books.csv  
  Columns: `ISBN`, `Book-Title`, `Book-Author`, `Year-Of-Publication`, `Publisher`, `Image-URL-S`, `Image-URL-M`, `Image-URL-L`
- BX-Book-Ratings.csv  
  Columns: `User-ID`, `ISBN`, `Book-Rating`
- final_rating.pkl  
  Pre‑processed ratings dataset used by the recommender.
- book_names.pkl, book_pivot.pkl, model.pkl  
  ML model and supporting data for recommendations.

3. Page Logic
 Home.py – Most Popular
1. Load `BX-Books.csv` and `BX-Book-Ratings.csv`.
2. Merge on `ISBN`.
3. Group by ISBN/title/author/image to calculate:
   - `avg_rating` (converted to /5 if >5)
   - `num_ratings`
4. Filter out books with fewer than 10 ratings.
5. Sort by `num_ratings` (descending).
6. Display top 50 in a 5‑column grid.

 TopRated.py* – Highest Average Rating
1. Same merge and aggregation as Home.py.
2. Slider to set minimum number of ratings.
3. Sort by `avg_rating` (descending).
4. Display top 50 in a 5‑column grid.

 Recommender.py – ML Recommendations
1. Load ML model and data (`model.pkl`, `book_names.pkl`, `final_rating.pkl`, `book_pivot.pkl`).
2. Load CSVs for rating calculation (same as Home/TopRated).
3. When a book is selected:
   - Find similar books using `model.kneighbors`.
   - For each recommendation:
     - Get image from `final_rating.pkl` or placeholder.
     - Calculate rating from merged CSVs (no Google API ratings).
     - Get ISBN from dataset if available.
     - Get description from dataset or Google Books API (only for description).
4. Display recommendations in a row with image, title, rating, ISBN link, and description.

 4. Clickable ISBN Links
- All pages use:
  ```python
  st.markdown(f"[ISBN: {isbn}](https://www.google.com/search?q=isbn+{isbn})")
  ```
- This opens a normal Google search in the “All” tab, avoiding the broken Books tab.
