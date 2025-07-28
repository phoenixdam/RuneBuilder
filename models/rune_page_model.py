import json
from typing import List, Dict, Tuple, Optional, Any
from models.database_model import DatabaseModel


class RunePageModel:
    """Model for managing rune page data and operations"""
    
    def __init__(self, db_model: DatabaseModel):
        self.db_model = db_model
        
    def save_rune_page(self, name: str, champion_id: int, primary_tree: str, 
                      secondary_tree: str, keystone: str, primary_runes: Dict,
                      secondary_runes: Dict, stat_shards: Dict, notes: str = "",
                      is_default: bool = False) -> None:
        """Save a new rune page to the database"""
        self.db_model.execute_query('''
            INSERT INTO rune_pages 
            (name, champion_id, primary_tree, secondary_tree, keystone, 
             primary_runes, secondary_runes, stat_shards, notes, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, champion_id, primary_tree, secondary_tree, keystone,
            json.dumps(primary_runes), json.dumps(secondary_runes),
            json.dumps(stat_shards), notes, is_default
        ))
        
    def get_champion_rune_pages(self, champion_id: int) -> List[Tuple]:
        """Get all rune pages for a champion, sorted by default first"""
        return self.db_model.execute_query('''
            SELECT id, name, primary_tree, secondary_tree, keystone, notes, is_default
            FROM rune_pages 
            WHERE champion_id = ?
            ORDER BY is_default DESC, primary_tree, secondary_tree
        ''', (champion_id,), fetch_all=True)
        
    def get_rune_page_by_id(self, page_id: int) -> Optional[Tuple]:
        """Get complete rune page data by ID"""
        return self.db_model.execute_query('''
            SELECT id, name, primary_tree, secondary_tree, keystone, primary_runes, 
                   secondary_runes, stat_shards, notes
            FROM rune_pages 
            WHERE id = ?
        ''', (page_id,), fetch_one=True)
        
    def get_default_rune_page(self, champion_id: int) -> Optional[Tuple]:
        """Get default rune page for a champion"""
        return self.db_model.execute_query('''
            SELECT primary_tree, secondary_tree, keystone, primary_runes, 
                   secondary_runes, stat_shards
            FROM rune_pages 
            WHERE champion_id = ? AND is_default = 1
            LIMIT 1
        ''', (champion_id,), fetch_one=True)
        
    def set_as_default(self, page_id: int, champion_id: int) -> None:
        """Toggle a rune page as the default for a champion"""
        # Check if this page is already default
        is_currently_default = self.is_page_default(page_id)
        
        if is_currently_default:
            # If already default, remove default status
            self.db_model.execute_query(
                "UPDATE rune_pages SET is_default = 0 WHERE id = ?",
                (page_id,)
            )
        else:
            # Remove default from all other pages for this champion
            self.db_model.execute_query(
                "UPDATE rune_pages SET is_default = 0 WHERE champion_id = ?",
                (champion_id,)
            )
            
            # Set this page as default
            self.db_model.execute_query(
                "UPDATE rune_pages SET is_default = 1 WHERE id = ?",
                (page_id,)
            )
    
    def is_page_default(self, page_id: int) -> bool:
        """Check if a rune page is currently set as default"""
        result = self.db_model.execute_query(
            "SELECT is_default FROM rune_pages WHERE id = ?",
            (page_id,), fetch_one=True
        )
        return bool(result[0]) if result else False
        
    def update_rune_page(self, page_id: int, name: str, champion_id: int, 
                         primary_tree: str, secondary_tree: str, keystone: str,
                         primary_runes: Dict, secondary_runes: Dict, stat_shards: Dict,
                         notes: str = "") -> None:
        """Update an existing rune page"""
        self.db_model.execute_query('''
            UPDATE rune_pages SET 
            name = ?, champion_id = ?, primary_tree = ?, secondary_tree = ?, 
            keystone = ?, primary_runes = ?, secondary_runes = ?, 
            stat_shards = ?, notes = ?
            WHERE id = ?
        ''', (
            name, champion_id, primary_tree, secondary_tree, keystone,
            json.dumps(primary_runes), json.dumps(secondary_runes),
            json.dumps(stat_shards), notes, page_id
        ))
    
    def delete_rune_page(self, page_id: int) -> None:
        """Delete a rune page"""
        self.db_model.execute_query("DELETE FROM rune_pages WHERE id = ?", (page_id,))
        
    def parse_rune_page_data(self, result: Tuple) -> Dict:
        """Parse database result into rune page data structure"""
        if not result:
            return {}
        
        # Handle different result formats for backward compatibility
        if len(result) == 6:
            # Old format (for default rune page)
            primary_tree, secondary_tree, keystone, primary_runes, secondary_runes, stat_shards = result
            data = {
                'primary_tree': primary_tree,
                'secondary_tree': secondary_tree,
                'keystone': keystone,
                'primary_runes': json.loads(primary_runes) if primary_runes else {},
                'secondary_runes': json.loads(secondary_runes) if secondary_runes else {},
                'stat_shards': json.loads(stat_shards) if stat_shards else {}
            }
        else:
            # New format (with id, name, notes)
            page_id, name, primary_tree, secondary_tree, keystone, primary_runes, secondary_runes, stat_shards, notes = result
            data = {
                'id': page_id,
                'name': name,
                'primary_tree': primary_tree,
                'secondary_tree': secondary_tree,
                'keystone': keystone,
                'primary_runes': json.loads(primary_runes) if primary_runes else {},
                'secondary_runes': json.loads(secondary_runes) if secondary_runes else {},
                'stat_shards': json.loads(stat_shards) if stat_shards else {},
                'notes': notes or ''
            }
        
        return data