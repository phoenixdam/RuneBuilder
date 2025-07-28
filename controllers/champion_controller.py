import os
from typing import List, Tuple, Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.champion_model import ChampionModel
from models.rune_page_model import RunePageModel
from models.profile_model import ProfileModel
from views.champion_view import ChampionView
from controllers.profile_controller import ProfileController
from .rune_state import RuneState


class ChampionController:
    """Controller for champion selection and related operations"""
    
    def __init__(self, champion_model: ChampionModel, rune_page_model: RunePageModel,
                 champion_view: ChampionView, rune_state: RuneState, 
                 profile_model: ProfileModel, image_loader):
        self.champion_model = champion_model
        self.rune_page_model = rune_page_model
        self.champion_view = champion_view
        self.rune_state = rune_state
        self.champions_data: List[Tuple] = []
        self.filtered_champions_data: List[Tuple] = []
        
        # Initialize profile controller
        self.profile_controller = ProfileController(profile_model, image_loader)
        
        # Set up callbacks
        self.champion_view.set_champion_select_callback(self.on_champion_selected)
        self.champion_view.set_search_callback(self.on_search_changed)
        self.champion_view.set_profile_callbacks(
            on_create=self.on_create_profile,
            on_edit=self.on_edit_profile,
            on_filter=self.on_filter_by_profile
        )
        self.champion_view.set_champion_matchups_callback(self.get_champion_matchups)
        
        # Set profile controller callbacks
        self.profile_controller.set_callbacks(
            on_created=self.on_profile_created,
            on_updated=self.on_profile_updated,
            on_deleted=self.on_profile_deleted
        )
        
        # Callbacks to notify other controllers
        self.on_champion_changed: Optional[callable] = None
        
    def initialize(self):
        """Initialize champion data"""
        # Load existing champions
        self.load_champions()
        # Load existing profiles
        self.load_profiles()
        
    def load_champions(self):
        """Load and display champions with rune counts"""
        self.champions_data = self.champion_model.get_champions_with_rune_counts()
        self.filtered_champions_data = self.champions_data
        self.profile_controller.set_champions_data(self.champions_data)
        self.champion_view.set_champions_data(self.champions_data)
        self.champion_view.display_champions(self.champions_data)
        
    def refresh_champions(self):
        """Refresh champion list while preserving current profile filter and selected champion"""
        # Store current states
        current_filter_profile_id = self.champion_view.current_filter_profile_id
        current_selected_champion = self.champion_view.last_selected_champion
        
        # Reload champion data
        self.champions_data = self.champion_model.get_champions_with_rune_counts()
        self.profile_controller.set_champions_data(self.champions_data)
        self.champion_view.set_champions_data(self.champions_data)
        
        # Restore profile filter if one was active
        if current_filter_profile_id:
            self.on_filter_by_profile(current_filter_profile_id)
        else:
            self.filtered_champions_data = self.champions_data
            self.champion_view.display_champions(self.champions_data)
        
        # Always restore the visual state of profile buttons regardless of filter state
        self.champion_view.update_selected_profile(current_filter_profile_id)
        
        # Restore selected champion visual state
        if current_selected_champion:
            self.champion_view.update_selected_champion(current_selected_champion)
        
    def on_champion_selected(self, champion_id: int, champion_name: str):
        """Handle champion selection or deselection"""
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
        # Use filtered_champions_data to respect profile filters
        for champion_id, name, image_path, rune_count in self.filtered_champions_data:
            if search_filter.lower() in name.lower():
                matching_champions.append((champion_id, name, image_path, rune_count))
        return matching_champions
    
    def load_profiles(self):
        """Load and display all profiles"""
        profiles = self.profile_controller.get_all_profiles()
        for profile_id, profile_name in profiles:
            champion_data = self.profile_controller.get_profile_champions(profile_id)
            champion_names = [name for _, name in champion_data]
            champion_ids = self.profile_controller.get_profile_champion_ids(profile_id)
            self.champion_view.set_profile_champion_data(profile_id, champion_ids)
            self.champion_view.add_profile_button(profile_id, profile_name, champion_names)
    
    def on_create_profile(self):
        """Handle create profile request"""
        # Get the parent window for the dialog
        parent = self.champion_view.parent.winfo_toplevel()
        self.profile_controller.show_create_profile_dialog(parent)
    
    def on_edit_profile(self, profile_id: int):
        """Handle edit profile request"""
        # Get the parent window for the dialog
        parent = self.champion_view.parent.winfo_toplevel()
        self.profile_controller.show_edit_profile_dialog(parent, profile_id)
    
    def on_filter_by_profile(self, profile_id: Optional[int]):
        """Handle profile filter request"""
        if profile_id is None:
            # Show all champions
            self.filtered_champions_data = self.champions_data
        else:
            # Filter to profile champions
            profile_champion_ids = set(self.profile_controller.get_profile_champion_ids(profile_id))
            self.filtered_champions_data = [
                champion for champion in self.champions_data 
                if champion[0] in profile_champion_ids
            ]
        
        # Refresh the display with current search
        self.on_search_changed()
    
    def on_profile_created(self, profile_id: int):
        """Handle profile creation"""
        profile_info = self.profile_controller.profile_model.get_profile_by_id(profile_id)
        if profile_info:
            _, profile_name = profile_info
            champion_data = self.profile_controller.get_profile_champions(profile_id)
            champion_names = [name for _, name in champion_data]
            champion_ids = self.profile_controller.get_profile_champion_ids(profile_id)
            self.champion_view.set_profile_champion_data(profile_id, champion_ids)
            self.champion_view.add_profile_button(profile_id, profile_name, champion_names)
    
    def on_profile_updated(self, profile_id: int):
        """Handle profile update"""
        profile_info = self.profile_controller.profile_model.get_profile_by_id(profile_id)
        if profile_info:
            _, profile_name = profile_info
            champion_data = self.profile_controller.get_profile_champions(profile_id)
            champion_names = [name for _, name in champion_data]
            champion_ids = self.profile_controller.get_profile_champion_ids(profile_id)
            self.champion_view.set_profile_champion_data(profile_id, champion_ids)
            self.champion_view.update_profile_button(profile_id, profile_name, champion_names)
            
            # If this is the currently filtered profile, refresh the display
            if self.champion_view.current_filter_profile_id == profile_id:
                self.on_filter_by_profile(profile_id)
    
    def on_profile_deleted(self, profile_id: int):
        """Handle profile deletion"""
        self.champion_view.remove_profile_button(profile_id)
        
        # If this was the filtered profile, clear the filter
        if self.champion_view.current_filter_profile_id == profile_id:
            self.champion_view.clear_profile_filter()
            self.on_filter_by_profile(None)
        
    def set_champion_changed_callback(self, callback: callable):
        """Set callback for when champion selection changes"""
        self.on_champion_changed = callback
        
    def get_champion_matchups(self, champion_id: int) -> List[str]:
        """Get saved matchup names for a champion (for tooltips)"""
        try:
            rune_pages = self.rune_page_model.get_champion_rune_pages(champion_id)
            return [name for _, name, _, _, _, _, _ in rune_pages]
        except:
            return []
        
