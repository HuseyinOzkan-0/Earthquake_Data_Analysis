#!/usr/bin/env python
"""
Database management script for Earthquake Data Analysis
Provides utilities to clear, refresh, and manage the earthquake database
"""

import sys
from app import app, db, Earthquake, scrape_kandilli

def clear_database():
    """Delete all earthquake records from the database"""
    with app.app_context():
        db.session.query(Earthquake).delete()
        db.session.commit()
        print("Database cleared successfully!")

def refresh_database():
    """Clear and re-scrape all earthquake data"""
    with app.app_context():
        clear_database()
        print("Scraping new earthquake data...")
        scrape_kandilli()
        count = db.session.query(Earthquake).count()
        print(f"Loaded {count} earthquakes into database!")

def init_database():
    """Initialize a fresh database with tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def show_stats():
    """Display database statistics"""
    with app.app_context():
        total = db.session.query(Earthquake).count()
        anomalies = db.session.query(Earthquake).filter_by(is_anomaly=True).count()
        
        print(f"\nDatabase Statistics:")
        print(f"  Total Earthquakes: {total}")
        print(f"  Anomalies Detected: {anomalies}")
        
        if total > 0:
            avg_mag = db.session.query(db.func.avg(Earthquake.mag)).scalar()
            max_mag = db.session.query(db.func.max(Earthquake.mag)).scalar()
            print(f"  Average Magnitude: {avg_mag:.2f}")
            print(f"  Max Magnitude: {max_mag:.2f}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py [command]")
        print("\nCommands:")
        print("  init      - Initialize database tables")
        print("  clear     - Clear all data from database")
        print("  refresh   - Clear and re-scrape all data")
        print("  stats     - Show database statistics")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_database()
    elif command == 'clear':
        clear_database()
    elif command == 'refresh':
        refresh_database()
    elif command == 'stats':
        show_stats()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
