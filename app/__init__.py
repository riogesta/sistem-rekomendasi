from flask import Flask, g
from flask_minify import Minify
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
Minify(app=app, html=True, js=True)
app.secret_key = 'rahasianegara'

app.config['DATABASE'] = 'app/sisrekomendasi.sqlite'

# fungsi untuk membuat koneksi ke SQLite
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
def init_table_users():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # check ketersediaan tabel users
        if not check_table(cursor, 'users'):
            # tabel tidak ada, inisialisasi tabel
            with app.open_resource('models/users.sql', mode='r') as f:
                cursor.executescript(f.read())
            db.commit()
        
def check_table(cursor, table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
    return result is not None
    

init_table_users()

bcrypt = Bcrypt(app)

# from app.routes import routes
from app.routes.authentication_routes import login
app.register_blueprint(login, url_prefix='/login')
    
from app.routes.user_routes import users
app.register_blueprint(users, url_prefix='/users')

from app.routes.data_routes import data
app.register_blueprint(data, url_prefix='/data')

from app.routes.channel_routes import channel
app.register_blueprint(channel, url_prefix='/channels')
