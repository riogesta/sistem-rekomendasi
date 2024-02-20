from app import get_db

def is_user_rated(id):
    query = f"""
    SELECT
        users.id AS user_id,
        users.username,
        channels.channel
    FROM
        channels
    JOIN
        ratings ON ratings.channel_id = channels.channel_id
    JOIN
        users ON users.id = ratings.user_id
        
    WHERE user_id={id}
    """
    cursor = get_db().execute(query)
    cursor = cursor.fetchall()
    return cursor

def sum_user_rated(id):
    query = f"""
    SELECT
        SUM(ratings.rating) as sum_rating
    FROM
        channels
    JOIN
        ratings ON ratings.channel_id = channels.channel_id
    JOIN
        users ON users.id = ratings.user_id
        
    WHERE user_id={id}
    """
    cursor = get_db().execute(query)
    cursor = cursor.fetchone()
    return cursor['sum_rating']
