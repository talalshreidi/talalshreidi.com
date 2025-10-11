import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

def get_db_path():
    """Get the database file path in the instance folder"""
    instance_folder = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_folder):
        os.makedirs(instance_folder)
    return os.path.join(instance_folder, 'jobs.db')

def init_db():
    """Initialize the database with the jobs table"""
    conn = sqlite3.connect(get_db_path())
    # Create table with correct schema including tags column
    conn.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            url TEXT UNIQUE NOT NULL,
            tags TEXT,
            date_posted TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def is_db_initialized():
    """Check if the jobs table exists in the database"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    table_exists = cursor.fetchone() is not None
    conn.close()
    return table_exists

def clear_jobs():
    """Clear all jobs from the database"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs')
    conn.commit()
    conn.close()
    print("All jobs cleared from database")

def save_jobs(jobs_list):
    """Save jobs to the database"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    saved_count = 0
    for job in jobs_list:
        try:
            # Convert tags list to comma-separated string
            tags_str = ', '.join(job.get('tags', [])) if job.get('tags') else ''
            
            # Skip jobs without URLs
            job_url = job.get('link', '').strip()
            if not job_url:
                print(f"Skipping job without URL: {job.get('title', 'Unknown')}")
                continue
            
            cursor.execute('''
                INSERT INTO jobs (title, company, location, url, tags, date_posted, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.get('title', '').strip(),
                job.get('company', '').strip(),
                job.get('location', '').strip(),
                job_url,
                tags_str,
                job.get('time', '').strip(),
                datetime.now().isoformat()
            ))
            saved_count += 1
        except Exception as e:
            print(f"Error saving job: {e}")
            print(f"Job data: {job}")
    
    conn.commit()
    conn.close()
    print(f"Successfully saved {saved_count} jobs to database")
    return saved_count

def get_all_jobs():
    """Get all jobs from the database"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY scraped_at DESC")
    jobs = cursor.fetchall()
    
    conn.close()
    return [dict(job) for job in jobs]

# Add connection pooling and proper error handling
@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect('jobs.db', timeout=30)
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()