import os
import logging
from datetime import datetime, timezone, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from zoneinfo import ZoneInfo

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bathroom_queue.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Add timezone conversion filter
@app.template_filter('local_time')
def local_time_filter(utc_time):
    """Convert UTC time to local time for display"""
    if utc_time is None:
        return ''
    
    # Safely convert UTC-aware time to US Pacific Time
    local_time = utc_time.astimezone(ZoneInfo("America/Los_Angeles"))
    return local_time.strftime('%I:%M %p')

with app.app_context():
    # Import models here so tables are created
    import models
    db.create_all()

@app.route('/')
def index():
    """Display the bathroom queue and join form"""
    from models import QueueEntry
    
    # Get current queue entries ordered by join time
    queue_entries = QueueEntry.query.order_by(QueueEntry.joined_at).all()
    queue_count = len(queue_entries)
    is_full = queue_count >= 5
    
    return render_template('index.html', 
                         queue_entries=queue_entries, 
                         queue_count=queue_count,
                         is_full=is_full)

@app.route('/join', methods=['POST'])
def join_queue():
    """Add a student to the bathroom queue"""
    from models import QueueEntry
    
    student_name = request.form.get('student_name', '').strip()
    
    # Validate name input
    if not student_name:
        flash('Please enter your name.', 'error')
        return redirect(url_for('index'))
    
    if len(student_name) > 50:
        flash('Name is too long. Please use 50 characters or less.', 'error')
        return redirect(url_for('index'))
    
    # Check if queue is full
    current_count = QueueEntry.query.count()
    if current_count >= 5:
        flash('The bathroom queue is full. Please wait for someone to return.', 'error')
        return redirect(url_for('index'))
    
    # Check if student is already in queue
    existing_entry = QueueEntry.query.filter_by(student_name=student_name).first()
    if existing_entry:
        flash(f'{student_name} is already in the queue.', 'error')
        return redirect(url_for('index'))
    
    # Add student to queue
    new_entry = QueueEntry(student_name=student_name)
    db.session.add(new_entry)
    db.session.commit()
    
    flash(f'{student_name} has been added to the bathroom queue.', 'success')
    return redirect(url_for('index'))

@app.route('/checkout', methods=['POST'])
def checkout():
    """Remove a student from the bathroom queue"""
    from models import QueueEntry
    
    student_name = request.form.get('checkout_name', '').strip()
    
    if not student_name:
        flash('Please enter your name to check out.', 'error')
        return redirect(url_for('index'))
    
    # Find and remove the student from queue
    entry = QueueEntry.query.filter_by(student_name=student_name).first()
    if not entry:
        flash(f'{student_name} is not currently in the queue.', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(entry)
    db.session.commit()
    
    flash(f'{student_name} has been checked out of the bathroom queue.', 'success')
    return redirect(url_for('index'))

@app.route('/clear_queue', methods=['POST'])
def clear_queue():
    """Clear all entries from the queue (for teacher use)"""
    from models import QueueEntry
    
    QueueEntry.query.delete()
    db.session.commit()
    
    flash('The bathroom queue has been cleared.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
