import sqlite3
import os
import json
import threading
from typing import List, Dict, Tuple, Optional, Any


class DatabaseModel:
    """Database model for managing SQLite operations and schema"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database with required tables and optimizations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create champions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS champions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                image_path TEXT NOT NULL
            )
        ''')
        
        # Create rune_pages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rune_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                champion_id INTEGER,
                primary_tree TEXT,
                secondary_tree TEXT,
                keystone TEXT,
                primary_runes TEXT,
                secondary_runes TEXT,
                stat_shards TEXT,
                notes TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (champion_id) REFERENCES champions (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_champion_name ON champions(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_champion_id ON rune_pages(champion_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_name ON rune_pages(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_default ON rune_pages(is_default)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_primary_tree ON rune_pages(primary_tree)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_secondary_tree ON rune_pages(secondary_tree)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_created_date ON rune_pages(created_date)')
        
        # Composite indexes for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_champion_rune_pages ON rune_pages(champion_id, is_default)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tree_combination ON rune_pages(primary_tree, secondary_tree)')
        
        # Optimize database for better performance
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.execute('PRAGMA cache_size=10000')
        cursor.execute('PRAGMA temp_store=MEMORY')
        cursor.execute('PRAGMA mmap_size=268435456')
        
        conn.commit()
        conn.close()
        
    def execute_query(self, query: str, params: Tuple = (), fetch_one: bool = False, fetch_all: bool = False, executemany: bool = False) -> Any:
        """Execute database query with consistent connection handling"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if executemany:
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None
                
            conn.commit()
            return result
        finally:
            conn.close()
            
    def optimize_database_background(self):
        """Run database optimization in background thread"""
        def optimize():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('ANALYZE')
                cursor.execute('VACUUM')
                conn.commit()
                conn.close()
            except Exception:
                pass
        
        thread = threading.Thread(target=optimize, daemon=True)
        thread.start()