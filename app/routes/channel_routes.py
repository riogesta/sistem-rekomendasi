from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import get_db

channel = Blueprint('channel', __name__)

@channel.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        
        cursor = get_db().execute("SELECT * FROM channels")
        channels = cursor.fetchall()
    
        return render_template(
            './pages/channel.html',
            channels = channels
        )
        
    if request.method == 'POST':
        import uuid
        
        channel = request.form['channel']
        subscriber = request.form['subscriber']
        total_video = request.form['total_video']
        link = request.form['link']
        join_date = request.form['join_date']
        
        if channel == '' :
            flash('Data not successfully saved!', 'error')    
            return redirect(url_for('channel.index'))
        id = int(uuid.uuid4().hex[:8], base=16)
        
        db = get_db()
        db.execute(f"INSERT INTO channels (channel_id, channel, subscriber, total_video, link, join_date) VALUES ('{id}', '{channel}', '{subscriber}', '{total_video}', '{link}', '{join_date}')")
        db.commit()
        
        flash('Data successfully saved!', 'success')
        return redirect(url_for('channel.index'))
    
@channel.route('/<int:id>', methods=['POST', 'GET'])
def update_channel(id):
    if request.method == 'GET':
        
        cursor = get_db().execute(f"SELECT * FROM channels WHERE channel_id='{id}'")
        channel = cursor.fetchone()
        
        return render_template(
            './pages/edit_channel.html',
            channel = channel
        )
        
    if request.method == 'POST':
            
        channel = request.form['channel']
        subscriber = request.form['subscriber']
        total_video = request.form['total_video']
        link = request.form['link']
        join_date = request.form['join_date']
        
        if id and channel:
            get_db().execute(f"UPDATE channels SET channel = '{channel}', subscriber = '{subscriber}', total_video = '{total_video}', link = '{link}', join_date = '{join_date}' WHERE channel_id = '{id}'")
            get_db().commit()
            
        flash('Data successfully updated!', 'success')
        return redirect(url_for('channel.index'))
    
@channel.route('/delete/<int:id>')
def delete(id):
        
    get_db().execute(f"DELETE FROM channels WHERE channel_id='{id}'")
    get_db().commit()
    
    flash('Data successfully deleted!', 'success')
    return redirect(url_for('channel.index'))