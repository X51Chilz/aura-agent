import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_path='aura_agent.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT UNIQUE NOT NULL,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                summary TEXT,
                status TEXT DEFAULT 'PENDING_REVIEW',
                conversation_history TEXT,
                draft_response TEXT,
                message_id TEXT,
                email_references TEXT,
                thread_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add new columns if they don't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE email_threads ADD COLUMN message_id TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE email_threads ADD COLUMN email_references TEXT')
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute('ALTER TABLE email_threads ADD COLUMN thread_id TEXT')
        except sqlite3.OperationalError:
            pass
        
        conn.commit()
        conn.close()
    
    def create_thread(self, email_id, sender, subject, body, summary, message_id=None, references=None, thread_id=None):
        """Create a new email thread"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO email_threads (email_id, sender, subject, body, summary, conversation_history, message_id, email_references, thread_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email_id, sender, subject, body, summary, json.dumps([]), message_id, references, thread_id))
        
        thread_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return thread_db_id
    
    def get_thread_by_email_id(self, email_id):
        """Get thread by email ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_threads WHERE email_id = ?', (email_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_pending_threads(self):
        """Get all threads pending review"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_threads WHERE status = "PENDING_REVIEW"')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_conversation(self, email_id, conversation_history):
        """Update conversation history for a thread"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE email_threads 
            SET conversation_history = ?, updated_at = CURRENT_TIMESTAMP
            WHERE email_id = ?
        ''', (json.dumps(conversation_history), email_id))
        
        conn.commit()
        conn.close()
    
    def update_draft_response(self, email_id, draft_response):
        """Update draft response for a thread"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE email_threads 
            SET draft_response = ?, updated_at = CURRENT_TIMESTAMP
            WHERE email_id = ?
        ''', (draft_response, email_id))
        
        conn.commit()
        conn.close()
    
    def update_status(self, email_id, status):
        """Update status of a thread"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE email_threads 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE email_id = ?
        ''', (status, email_id))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, email_id):
        """Get conversation history as list"""
        thread = self.get_thread_by_email_id(email_id)
        if thread and thread['conversation_history']:
            return json.loads(thread['conversation_history'])
        return []
