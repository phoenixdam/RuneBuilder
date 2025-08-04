import os
import glob
from typing import List, Dict, Tuple, Optional
from models.database_model import DatabaseModel


class ChampionModel:
    """Model for managing champion data and operations"""
    
    def __init__(self, db_model: DatabaseModel):
        self.db_model = db_model
        
    def populate_champions_from_files(self, champions_dir: str) -> None:
        """Populate champions table from existing champion images"""
        if not os.path.exists(champions_dir):
            return
            
        # Get existing champions to avoid duplicates
        existing_champions = self.get_existing_champion_names()
        
        # Collect new champions to add in batch
        new_champions = []
        for filename in os.listdir(champions_dir):
            if filename.endswith('.png') and filename.startswith('42px-'):
                champion_name = self._extract_champion_name_from_file(filename)
                if champion_name and champion_name not in existing_champions:
                    # Always store the path relative to the project root (e.g., data/champion_icons/42px-Name_OriginalSquare.png)
                    rel_path = os.path.join('data', 'champion_icons', filename)
                    new_champions.append((champion_name, rel_path))
                    
        # Batch insert new champions
        if new_champions:
            self._batch_add_champions(new_champions)
                    
    def _extract_champion_name_from_file(self, filename: str) -> Optional[str]:
        """Extract champion name from filename and normalize it"""
        # Format: 42px-Champion_Name_OriginalSquare.png
        name_part = filename[5:-4]  # Remove "42px-" and ".png"
        if name_part.endswith('_OriginalSquare'):
            champion_name = name_part[:-14]  # Remove "_OriginalSquare"
            champion_name = champion_name.replace('_', ' ')
            return self._normalize_champion_name(champion_name)
        return None
        
    def _normalize_champion_name(self, champion_name: str) -> str:
        """Normalize champion names for special cases"""
        # Always strip whitespace first
        champion_name = champion_name.strip()
        
        champion_fixes = {
            "Cho'Gath": "Cho'Gath", "Dr. Mundo": "Dr. Mundo", "Jarvan IV": "Jarvan IV",
            "Master Yi": "Master Yi", "Miss Fortune": "Miss Fortune", "Aurelion Sol": "Aurelion Sol",
            "Lee Sin": "Lee Sin", "Twisted Fate": "Twisted Fate", "Xin Zhao": "Xin Zhao",
            "Renata Glasc": "Renata Glasc"
        }
        return champion_fixes.get(champion_name, champion_name)
        
    def get_existing_champion_names(self) -> set:
        """Get set of existing champion names from database"""
        result = self.db_model.execute_query("SELECT name FROM champions", fetch_all=True)
        return {row[0] for row in result} if result else set()
        
    def add_champion(self, name: str, image_path: str) -> None:
        """Add a new champion to the database"""
        self.db_model.execute_query(
            "INSERT INTO champions (name, image_path) VALUES (?, ?)",
            (name, image_path)
        )
        
    def get_champions_with_rune_counts(self) -> List[Tuple]:
        """Get champions ordered by rune page count then alphabetically"""
        return self.db_model.execute_query('''
            SELECT c.id, c.name, c.image_path, COUNT(rp.id) as rune_count
            FROM champions c
            LEFT JOIN rune_pages rp ON c.id = rp.champion_id
            GROUP BY c.id, c.name, c.image_path
            ORDER BY rune_count DESC, c.name ASC
        ''', fetch_all=True)
        
    def get_champion_by_id(self, champion_id: int) -> Optional[Tuple]:
        """Get champion by ID"""
        return self.db_model.execute_query(
            "SELECT id, name, image_path FROM champions WHERE id = ?",
            (champion_id,), fetch_one=True
        )
        
    def search_champions(self, search_term: str) -> List[Tuple]:
        """Search champions by name"""
        return self.db_model.execute_query(
            "SELECT id, name, image_path FROM champions WHERE name LIKE ? ORDER BY name",
            (f"%{search_term}%",), fetch_all=True
        )
        
    def _batch_add_champions(self, champions: List[Tuple]) -> None:
        """Add multiple champions in a single transaction"""
        if not champions:
            return
            
        try:
            # Use executemany for batch insert
            self.db_model.execute_query(
                "INSERT INTO champions (name, image_path) VALUES (?, ?)",
                champions, executemany=True
            )
        except Exception as e:
            # Fallback to individual inserts if batch fails
            for name, image_path in champions:
                try:
                    self.add_champion(name, image_path)
                except:
                    continue  # Skip duplicates or errors

    def delete_champion(self, champion_id: int) -> None:
        """Delete a champion by ID"""
        self.db_model.execute_query(
            "DELETE FROM champions WHERE id = ?",
            (champion_id,)
        )