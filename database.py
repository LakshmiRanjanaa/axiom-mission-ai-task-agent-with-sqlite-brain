import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class TaskDatabase:
    """Handles SQLite operations for task management"""
    
    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with tasks table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_task(self, description: str, priority: str = 'medium') -> int:
        """Add a new task to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO tasks (description, priority) VALUES (?, ?)",
            (description, priority)
        )
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def get_all_tasks(self) -> List[Dict]:
        """Retrieve all tasks from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        
        conn.close()
        
        # Convert to list of dictionaries
        return [
            {
                'id': task[0],
                'description': task[1],
                'priority': task[2],
                'status': task[3],
                'created_at': task[4]
            }
            for task in tasks
        ]
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """Update task status (pending, completed, cancelled)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted