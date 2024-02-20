from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app import app, bcrypt, get_db

login = Blueprint('auth', __name__)

@login.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        
        if session.get('logged_in') :
            # return f"session {session}"
            if session.get('role') == 0:
                return redirect(url_for('dashboard'))
            return redirect(url_for('recommendations'))
        
        return render_template(
            './pages/login.html'
        )
        
    if request.method == 'POST':
        
        data = request.form
        cursor = get_db().execute(f"SELECT * FROM users WHERE username='{data['username']}'")
        user = cursor.fetchone()
        
        if user is not None:
            if bcrypt.check_password_hash(user['password'], data['password']):
                session['logged_in'] = True
                session['username'] = data['username']
                session['role'] = user['role']
                flash('Signed in successfully', 'success')
                return redirect(url_for('auth.index'))
                
            else :
                flash("Password wrong! Try again", "error")
                return redirect(url_for('auth.index'))
            
        else:
            flash("Username not available!", "error")
            return redirect(url_for('auth.index'))

@login.route('/destroy', methods=['GET'])
def destroy_session():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    
    return redirect(url_for('auth.index'))