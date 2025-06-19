#!/usr/bin/env python3
"""
Database migration script to add owner_token column to existing QueueEntry tables.
This script should be run once to update existing databases.
"""

import os
import sys
from sqlalchemy import text

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import QueueEntry

def migrate_database():
    """Migrate the database to add owner_token column"""
    with app.app_context():
        # Check if the owner_token column already exists
        try:
            # Try to query the owner_token column
            result = db.session.execute(text("SELECT owner_token FROM queue_entry LIMIT 1"))
            print("✅ owner_token column already exists. Migration not needed.")
            return
        except Exception as e:
            if "no such column" in str(e).lower():
                print("🔄 owner_token column not found. Starting migration...")
            else:
                print(f"❌ Error checking column: {e}")
                return

        try:
            # Add the owner_token column
            db.session.execute(text("ALTER TABLE queue_entry ADD COLUMN owner_token VARCHAR(64)"))
            
            # Update existing entries with random tokens
            from models import QueueEntry
            entries = QueueEntry.query.all()
            for entry in entries:
                entry.owner_token = QueueEntry.generate_token()
            
            db.session.commit()
            print(f"✅ Successfully migrated {len(entries)} existing entries.")
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            return

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    migrate_database()
    print("🏁 Migration script finished.") 