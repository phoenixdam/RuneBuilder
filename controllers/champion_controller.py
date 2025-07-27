import os
from typing import List, Tuple, Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.champion_model import ChampionModel
from models.rune_page_model import RunePageModel
from views.champion_view import ChampionView
from .rune_state import RuneState


class ChampionController:
    """Controller for champion selection and related operations"""
    
    def __init__(self, champion_model: ChampionModel, rune_page_model: RunePageModel,
                 champion_view: ChampionView, rune_state: RuneState):
        self.champion_model = champion_model
        self.rune_page_model = rune_page_model
        self.champion_view = champion_view
        self.rune_state = rune_state
        self.champions_data: List[Tuple] = []
        
        # Set up callbacks
        self.champion_view.set_champion_select_callback(self.on_champion_selected)
        self.champion_view.set_search_callback(self.on_search_changed)
        
        # Callbacks to notify other controllers
        self.on_champion_changed: Optional[callable] = None
        
    def initialize(self):
        """Initialize champion data and populate from files"""
        # Populate champions from image files
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        champions_dir = os.path.join(script_dir, 'data', 'champion_icons')
        self.champion_model.populate_champions_from_files(champions_dir)
        
        # Load and display champions
        self.load_champions()
        
    def load_champions(self):
        """Load and display champions with rune counts"""
        self.champions_data = self.champion_model.get_champions_with_rune_counts()
        self.champion_view.display_champions(self.champions_data)
        
    def on_champion_selected(self, champion_id: int, champion_name: str):
        """Handle champion selection"""
        self.rune_state.set_champion(champion_id, champion_name)
        self.champion_view.update_selected_champion(champion_id)
        
        # Notify other controllers about champion change
        if self.on_champion_changed:
            self.on_champion_changed(champion_id)
            
    def on_search_changed(self, *args):
        """Handle search text changes"""
        search_text = self.champion_view.get_search_text()
        matching_champions = self._filter_champions_by_name(search_text)
        self.champion_view.display_champions(matching_champions)
        
    def _filter_champions_by_name(self, search_filter: str) -> List[Tuple]:
        """Filter champions by search term"""
        matching_champions = []
        for champion_id, name, image_path, rune_count in self.champions_data:
            if search_filter.lower() in name.lower():
                matching_champions.append((champion_id, name, image_path, rune_count))
        return matching_champions
        
    def set_champion_changed_callback(self, callback: callable):
        """Set callback for when champion selection changes"""
        self.on_champion_changed = callback