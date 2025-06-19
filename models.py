from datetime import datetime, timezone
import secrets
from extensions import db

class QueueEntry(db.Model):
    """Model for bathroom queue entries"""
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    joined_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    owner_token = db.Column(db.String(64), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<QueueEntry {self.student_name}>'
    
    def get_position(self):
        """Get the position of this student in the queue (1-based)"""
        earlier_entries = QueueEntry.query.filter(QueueEntry.joined_at < self.joined_at).count()
        return earlier_entries + 1
    
    @staticmethod
    def generate_token():
        """Generate a unique token for entry ownership"""
        return secrets.token_urlsafe(32)



