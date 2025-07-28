import json
from typing import List, Dict, Tuple, Optional
from models.database_model import DatabaseModel


class ProfileModel:
    """Model for managing champion profiles"""
    
    def __init__(self, db_model: DatabaseModel):
        self.db_model = db_model
        self._create_profile_tables()
        
    def _create_profile_tables(self):
        """Create profile tables if they don't exist"""
        # Create profiles table
        self.db_model.execute_query('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create profile_champions junction table
        self.db_model.execute_query('''
            CREATE TABLE IF NOT EXISTS profile_champions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                champion_id INTEGER NOT NULL,
                FOREIGN KEY (profile_id) REFERENCES profiles (id) ON DELETE CASCADE,
                FOREIGN KEY (champion_id) REFERENCES champions (id) ON DELETE CASCADE,
                UNIQUE(profile_id, champion_id)
            )
        ''')
        
    def save_profile(self, name: str, champion_ids: List[int]) -> int:
        """Save a new profile with champion IDs"""
        # Insert profile using direct connection to get lastrowid
        import sqlite3
        conn = sqlite3.connect(self.db_model.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO profiles (name) VALUES (?)", (name,))
            profile_id = cursor.lastrowid
            
            # Insert champion associations
            for champion_id in champion_ids:
                cursor.execute(
                    "INSERT OR IGNORE INTO profile_champions (profile_id, champion_id) VALUES (?, ?)",
                    (profile_id, champion_id)
                )
            
            conn.commit()
            return profile_id
        finally:
            conn.close()
    
    def update_profile(self, profile_id: int, name: str, champion_ids: List[int]) -> None:
        """Update an existing profile"""
        # Use direct connection for batch operations
        import sqlite3
        conn = sqlite3.connect(self.db_model.db_path)
        cursor = conn.cursor()
        
        try:
            # Update profile name
            cursor.execute("UPDATE profiles SET name = ? WHERE id = ?", (name, profile_id))
            
            # Clear existing champion associations
            cursor.execute("DELETE FROM profile_champions WHERE profile_id = ?", (profile_id,))
            
            # Insert new champion associations
            for champion_id in champion_ids:
                cursor.execute(
                    "INSERT INTO profile_champions (profile_id, champion_id) VALUES (?, ?)",
                    (profile_id, champion_id)
                )
            
            conn.commit()
        finally:
            conn.close()
    
    def get_all_profiles(self) -> List[Tuple[int, str]]:
        """Get all profiles with their basic info"""
        return self.db_model.execute_query(
            "SELECT id, name FROM profiles ORDER BY name",
            fetch_all=True
        )
    
    def get_profile_champions(self, profile_id: int) -> List[Tuple[int, str]]:
        """Get all champions in a profile"""
        return self.db_model.execute_query('''
            SELECT c.id, c.name 
            FROM champions c
            JOIN profile_champions pc ON c.id = pc.champion_id
            WHERE pc.profile_id = ?
            ORDER BY c.name
        ''', (profile_id,), fetch_all=True)
    
    def get_profile_by_id(self, profile_id: int) -> Optional[Tuple[int, str]]:
        """Get profile info by ID"""
        return self.db_model.execute_query(
            "SELECT id, name FROM profiles WHERE id = ?",
            (profile_id,), fetch_one=True
        )
    
    def delete_profile(self, profile_id: int) -> None:
        """Delete a profile and its champion associations"""
        self.db_model.execute_query(
            "DELETE FROM profiles WHERE id = ?",
            (profile_id,)
        )
        # Cascade delete will handle profile_champions
        
    def get_profile_champion_ids(self, profile_id: int) -> List[int]:
        """Get champion IDs for a profile"""
        result = self.db_model.execute_query(
            "SELECT champion_id FROM profile_champions WHERE profile_id = ?",
            (profile_id,), fetch_all=True
        )
        return [row[0] for row in result] if result else []