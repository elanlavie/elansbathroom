import os
import logging
import uuid
from datetime import datetime, timezone

from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from werkzeug.middleware.proxy_fix import ProxyFix

from extensions import db

# Handle zoneinfo import for different Python versions
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bathroom_queue.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Initialize extensions
    db.init_app(app)

    # Import models here to avoid circular imports
    from models import QueueEntry

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # --- Template Filters ---
    @app.template_filter('local_time')
    def local_time_filter(utc_dt):
        if not utc_dt:
            return ""
        local_tz = ZoneInfo("America/Los_Angeles")  # Pacific Time
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime('%-I:%M %p')

    # --- Routes ---
    @app.route('/')
    def index():
        queue_entries = QueueEntry.query.order_by(QueueEntry.joined_at).all()
        queue_count = len(queue_entries)
        is_full = queue_count >= 5
        
        user_token = request.cookies.get('bathroom_token')
        user_entry = None
        if user_token:
            user_entry = QueueEntry.query.filter_by(owner_token=user_token).first()
            if not user_entry:
                user_token = None
        
        return render_template(
            'index.html',
            queue_entries=queue_entries,
            queue_count=queue_count,
            is_full=is_full,
            user_token=user_token,
            user_entry=user_entry
        )

    @app.route('/join', methods=['POST'])
    def join_queue():
        if QueueEntry.query.count() >= 5:
            flash('The queue is full. Please wait.', 'warning')
            return redirect(url_for('index'))
            
        if request.cookies.get('bathroom_token'):
            existing_token = request.cookies.get('bathroom_token')
            if QueueEntry.query.filter_by(owner_token=existing_token).first():
                flash('This computer is already associated with an entry in the queue.', 'error')
                return redirect(url_for('index'))

        student_name = request.form.get('student_name')
        if not student_name or not student_name.strip():
            flash('Please enter a name.', 'error')
            return redirect(url_for('index'))

        if QueueEntry.query.filter_by(student_name=student_name).first():
            flash(f'"{student_name}" is already in the queue.', 'error')
            return redirect(url_for('index'))

        owner_token = str(uuid.uuid4())
        new_entry = QueueEntry(student_name=student_name, owner_token=owner_token)
        db.session.add(new_entry)
        db.session.commit()
        
        flash(f'"{student_name}" has been added to the queue.', 'success')
        response = make_response(redirect(url_for('index')))
        response.set_cookie('bathroom_token', owner_token, max_age=86400)
        return response

    @app.route('/checkout', methods=['POST'])
    def checkout():
        checkout_name = request.form.get('checkout_name')
        if not checkout_name:
            flash('Please provide a name to check out.', 'error')
            return redirect(url_for('index'))

        entry = QueueEntry.query.filter_by(student_name=checkout_name).first()
        if not entry:
            flash(f'"{checkout_name}" was not found in the queue.', 'error')
            return redirect(url_for('index'))

        user_token = request.cookies.get('bathroom_token')
        if entry.owner_token != user_token:
            flash('You do not have permission to check out this name.', 'error')
            return redirect(url_for('index'))

        db.session.delete(entry)
        db.session.commit()
        
        flash(f'"{checkout_name}" has been checked out.', 'success')
        response = make_response(redirect(url_for('index')))
        response.delete_cookie('bathroom_token')
        return response

    @app.route('/clear_queue', methods=['POST'])
    def clear_queue():
        try:
            num_rows_deleted = db.session.query(QueueEntry).delete()
            db.session.commit()
            if num_rows_deleted > 0:
                flash(f'The queue has been cleared ({num_rows_deleted} entries removed).', 'success')
            else:
                flash('The queue was already empty.', 'info')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while clearing the queue: {e}', 'error')
        
        response = make_response(redirect(url_for('index')))
        response.delete_cookie('bathroom_token')
        return response

    return app

# This allows running with `python app.py` for local development
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
