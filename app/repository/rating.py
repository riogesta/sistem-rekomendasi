from app import get_db

def get_current_user(username):
    return get_db().execute(f"SELECT * FROM users WHERE username='{username}'").fetchone()

def find_by_channel(channel_name):
    """
    find channel by channel name
    """
    query = f"SELECT * FROM channels WHERE channel = '{channel_name}'"
    cursor = get_db().execute(query)
    cursor = cursor.fetchone()
    return cursor

def find_channel_by_id(id_channel):
    """
    find channel by channel name
    """
    query = f"SELECT * FROM channels WHERE channel_id = '{id_channel}'"
    cursor = get_db().execute(query)
    cursor = cursor.fetchone()
    return cursor

def find_rated_channels(id_user, id_channel):
    query = f"""
    SELECT
        users.id AS user_id,
        users.username,
        channels.channel_id,
        channels.channel,
        ratings.rating
    FROM
        channels
    JOIN
        ratings ON ratings.channel_id = channels.channel_id
    JOIN
        users ON users.id = ratings.user_id
        
    WHERE user_id='{id_user}' AND channels.channel_id='{id_channel}'
    """
    cursor = get_db().execute(query)
    cursor = cursor.fetchone()
    return cursor

def give_rating(id_user, id_channel, rate):
    db = get_db()
    cursor = db.execute(f"SELECT * FROM ratings WHERE user_id='{id_user}' AND channel_id='{id_channel}'")
    rating = cursor.fetchall()
    
    if len(rating) > 0:
        db.execute(f"UPDATE ratings SET rating='{rate}' WHERE user_id='{id_user}' AND channel_id='{id_channel}'")
        db.commit()
    else:
        db.execute(f"INSERT INTO ratings (user_id, channel_id, rating) VALUES ('{id_user}', '{id_channel}', '{rate}')")
        db.commit()