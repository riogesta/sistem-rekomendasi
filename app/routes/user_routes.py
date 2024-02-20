from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import bcrypt, get_db
# from app.models.Users import Users

users = Blueprint('users', __name__)

@users.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        
        cursor = get_db().execute(f"SELECT * FROM users")
        users = cursor.fetchall()
        
        return render_template(
            'pages/user.html',
            data = users
        )
        
    if request.method == 'POST':
        data = request.form
        
        if data :
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf8') 
            db = get_db()
            db.execute(f"INSERT INTO users (username, password, role) VALUES ('{data['username']}', '{hashed_password}', '{data['role']}')")
            db.commit()
            del hashed_password
        
        flash('Data successfully saved!', 'success')
        return redirect(url_for('users.index'))
    
@users.route('/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    
    db = get_db()
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        pw_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        if new_username and new_password :
            db.execute(f"UPDATE users SET username = '{new_username}', password = '{pw_hash}' WHERE id = {id}")
            db.commit()
        
        flash('Data successfully updated!', 'success')    
        return redirect(url_for('users.index'))
    
    cursor = db.execute(f"SELECT * FROM users WHERE id = {id}")
    data_to_edit = cursor.fetchone()
    
    return render_template(
        'pages/edit_user.html',
        user = data_to_edit
    )
    
@users.route('/delete/<int:id>')
def delete(id):
    
    get_db().execute(f"DELETE FROM users WHERE id='{id}'")
    get_db().commit()
    
    flash('Data successfully deleted!', 'success')
    return redirect(url_for('users.index'))
        