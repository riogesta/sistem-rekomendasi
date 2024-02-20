from app import get_db
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def load_data():
    db = get_db()
    query = "SELECT * FROM channel_ratings_view"
    data = pd.read_sql(query, db)
    
    return data


def create_grafik():
    import matplotlib.pyplot as plt
    import json

    df = load_data()
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['rating'])
    average_ratings = df.groupby('channel')['rating'].mean().sort_values()
    channels = average_ratings.index.tolist()
    ratings = average_ratings.values.tolist()

    return (json.dumps(channels), json.dumps(ratings)) #
    # return {
    #     channels : json.dumps(channels),
    #     ratings : json.dumps(ratings)
    # }

    # plt.figure(figsize=(12,6))
    # average_ratings.sort_values().plot(kind='bar')
    # plt.title('Rata-Rata Rating per Channel')
    # plt.xlabel('Channel')
    # plt.ylabel('Rata-Rata Rating')
    # plt.xticks(rotation=45)
    # # plt.show()
    # plt.savefig("./app/static/assets/img/rating_avg.png")


def user_similarity(df):
    # Mendapatkan similarity scores untuk item tertentu
    df['channel'] = df['channel'].str.replace("'", "")
    # user_item_matrix = df.pivot_table(index='user_id', columns='channel', values='rating', fill_value=0)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['rating'])
    grouped = df.grouped = df.groupby(['user_id', 'channel'])['rating'].mean()
    user_item_matrix = grouped.unstack(fill_value=0)
    # return user_item_matrix.to_html()
    
    # Menghitung cosine similarity antar pengguna
    user_similarity = cosine_similarity(user_item_matrix)
    
    user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)
    
    return (user_item_matrix, user_similarity_df)

def get_user_recommendations(user_id, user_similarity, n=10):
    user_item_matrix = user_similarity[0]
    # Mendapatkan similarity scores untuk pengguna tertentu
    user_similarity_df = user_similarity[1]
    user_similarity_scores = user_similarity_df[user_id]

    # Melihat rating pengguna tertentu
    user_ratings = user_item_matrix.loc[user_id]
    
    # Menyusun DataFrame dengan film yang belum dilihat dan similarity score
    unseen_movies = user_ratings[user_ratings == 0].index
    recommendations_df = pd.DataFrame(index=unseen_movies)
    
    # Menghitung weighted average rating berdasarkan similarity scores
    for other_user_id in user_similarity_scores.index:
        if other_user_id != user_id:
            other_user_ratings = user_item_matrix.loc[other_user_id]
            weighted_ratings = other_user_ratings * user_similarity_scores[other_user_id]
            recommendations_df[other_user_id] = weighted_ratings
    
    # Menghitung rata-rata weighted rating
    recommendations_df['weighted_average'] = recommendations_df.sum(axis=1) / user_similarity_scores.sum()
    
    # Menampilkan n rekomendasi teratas
    top_recommendations = recommendations_df.sort_values(by='weighted_average', ascending=False).head(n)
    
    return top_recommendations

def calculate_mae(user_item_matrix, user_similarity_df):
    from sklearn.metrics import mean_absolute_error
    from sklearn.model_selection import train_test_split
    
    mae_values = []
    
    for user_id in user_item_matrix.index:
        actual_ratings = user_item_matrix.loc[user_id]
        
        # Mendapatkan rekomendasi untuk pengguna tertentu
        recommendations = get_user_recommendations(user_id, (user_item_matrix, user_similarity_df))
        
        # Hanya hitung MAE untuk channel yang ada di kedua dataframe
        common_channels = actual_ratings.index.intersection(recommendations.index)
        
        # Memilih rating yang sebenarnya dan yang diprediksi untuk channel yang sama
        actual_ratings = actual_ratings[common_channels]
        predicted_ratings = recommendations['weighted_average'][common_channels]

        # Hitung MAE
        mae = mean_absolute_error(actual_ratings, predicted_ratings)
        mae_values.append(mae)

    # Rata-rata dari semua nilai MAE
    average_mae = sum(mae_values) / len(mae_values)
    
    return average_mae
