from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import app, get_db
import app.repository.rating as repo_rating

data = Blueprint('data', __name__)

@app.route('/', methods=['GET'])
def recommendations():
    if not session:
        return redirect(url_for('auth.index'))
    import app.models.cf as cf
    
    db = get_db()
    channels = db.execute("SELECT * FROM channels")
    channels = channels.fetchall()
    
    cursor = get_db().execute(f"SELECT * FROM users WHERE username='{session['username']}'")
    user = dict(cursor.fetchone())
    
    from app.models.relations import is_user_rated, sum_user_rated
    condition  = is_user_rated(user['id'])
    
    if not len(condition) > 0:
        return render_template(
            './pages/rekomendasi.html'
        )
    
    data = cf.load_data()
    similarity = cf.user_similarity(data)
    data_recommendation = cf.get_user_recommendations(user['id'], similarity)
    
    rekomendasi = data_recommendation.index.to_list() 
    # Escape single quotes in each item
    rekomendasi_escaped = [item.replace("'", "''") for item in rekomendasi]
    # query = "SELECT * FROM channels WHERE channel IN ({})".format(','.join([f"'{item}'" for item in rekomendasi]))
    query = "SELECT * FROM channels WHERE channel IN ({})".format(','.join([f"'{item}'" for item in rekomendasi_escaped]))
    cursor = get_db().execute(query)
    rekomendasi = cursor.fetchall()
    
    sum_rating = sum_user_rated(user['id'])
    
    return render_template(
        './pages/rekomendasi.html',
        recommendations = rekomendasi,
        sum_channels = len(channels),
        count_rated = len(condition),
        sum_rating = sum_rating
    )

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session:
        return redirect(url_for('auth.index'))
    
    return render_template(
        "./pages/admin/dashboard.html"
    )

@data.route('/wa-similarity', methods=['GET', 'POST'])
def wa_similarity():
    
    db = get_db()
    cursor = db.execute("""
                SELECT
                    users.id,
                    username
                FROM 
                    users
                JOIN
                    ratings ON ratings.user_id = users.id
                JOIN
                    channels on channels.channel_id = ratings.channel_id

                GROUP BY username
                """)
    users = cursor.fetchall()
    
    if request.method == 'POST':
        
        import app.models.cf as cf
        id = request.form['user']
        
        if not id:
            return render_template(
                './pages/admin/wa_similarity.html',
                users = users
            )
        
        cursor = get_db().execute(f"SELECT * FROM users WHERE id='{id}'")
        user = cursor.fetchone()
        
        data = cf.load_data()
        similarity = cf.user_similarity(data)
        data_recommendation = cf.get_user_recommendations(user['id'], similarity)
        
        # user_item_similarity, user_similarity_df = similarity
        
        # return f"{user_similarity_df.to_html()}"
        return render_template(
            '/pages/admin/wa_similarity.html',
            users = users,
            user = user['username'],
            recommendations = data_recommendation.to_html(classes='table table-bordered', justify='left')
        )
    
    return render_template(
        './pages/admin/wa_similarity.html',
        users = users
    )

@data.route('/cosine-similarity', methods=['GET'])
def cosine_similarity():
    import app.models.cf as cf

    data = cf.load_data()
    similarity = cf.user_similarity(data)
    # return f"{similarity}"
    
    user_items_matrix = similarity[0]
    user_similarity = similarity[1]
    mae = cf.calculate_mae(similarity[0], similarity[1])
    
    channels, ratings  = cf.create_grafik()

    # return f"{user_similarity_df.to_html()}"
    return render_template(
        './pages/admin/cosine_similarity.html',
        matrix_items = user_items_matrix.to_html(classes='table table-bordered', justify='left'),
        cosine = user_similarity.to_html(classes='table table-bordered', justify='left'),
        mae = mae,
        channels = channels,
        ratings = ratings
    )

@data.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        
        return render_template(
            './pages/data.html'
        )
        
    if request.method == 'POST':
        import pandas as pd
        
        data = request.files['file']
        
        if data:
            df = pd.read_csv(data)
            
            # memasukan dataframe ke sqlite
            db = get_db()
            df.to_sql('channels', con=db, if_exists='replace', index=False)
            
        
        return redirect(url_for('data.index'))
    
@data.route('/channels', methods=['POST', 'GET'])
def channels():
    if request.method == 'GET':
        
        cursor = get_db().execute(f'SELECT * FROM channels')
        channels = cursor.fetchall()
        
        cursor = get_db().execute(f"SELECT * FROM users WHERE username = '{session['username']}'")
        user = cursor.fetchone()
        
        # query = f"""
        cursor = get_db().execute(f"""
                    SELECT
                        users.id AS user_id,
                        users.username,
                        channels.channel_id,
                        channels.channel,
                        channels.subscriber,
                        channels.total_video,
                        channels.link,
                        channels.join_date,
                        ratings.rating
                    FROM
                        channels
                    JOIN
                        ratings ON ratings.channel_id = channels.channel_id
                    JOIN
                        users ON users.id = ratings.user_id
                        
                    WHERE user_id='{user['id']}'                          
        """)
        channels_rated = cursor.fetchall()
        # import pandas as pd
        # channels_rated = pd.read_sql_query(query, get_db())
        # return f"{channels_rated.columns}"
        
        return render_template(
            './pages/produk.html',
            channels = channels,
            rated = channels_rated
        )

@data.route('/channels/<int:id_channel>', methods=['GET', 'POST'])
def give_rating(id_channel):
    current_user = repo_rating.get_current_user(session['username'])
    chl = repo_rating.find_rated_channels(id_user=current_user['id'], id_channel=id_channel)
    
    # return f"{dict(chl)}"
    if not chl:
        chl = repo_rating.find_channel_by_id(id_channel)
    
    if chl: 
        # return f"{dict(chl)}"
        if request.method == 'POST':
            data = request.form
            repo_rating.give_rating(id_user=current_user['id'], id_channel=chl['channel_id'], rate=data['rating'])
                
            flash('successfully rated!', 'success')    
            return redirect(url_for('data.channels'))
            
    
    return render_template(
        './pages/give_rating.html',
        channel = chl
    )