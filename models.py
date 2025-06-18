from datetime import datetime, timezone
from app import db

class QueueEntry(db.Model):
    """Model for bathroom queue entries"""
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    joined_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<QueueEntry {self.student_name}>'
    
    def get_position(self):
        """Get the position of this student in the queue (1-based)"""
        earlier_entries = QueueEntry.query.filter(QueueEntry.joined_at < self.joined_at).count()
        return earlier_entries + 1



