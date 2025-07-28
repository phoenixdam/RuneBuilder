import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tkinter import messagebox
from typing import List, Tuple, Optional
from models.rune_page_model import RunePageModel
from views.saved_runes_view import SavedRunesView
from .rune_state import RuneState


class SavedRunesController:
    """Controller for saved rune pages operations"""
    
    def __init__(self, rune_page_model: RunePageModel, saved_runes_view: SavedRunesView, rune_state: RuneState):
        self.rune_page_model = rune_page_model
        self.saved_runes_view = saved_runes_view
        self.rune_state = rune_state
        
        # Set up callbacks
        self.saved_runes_view.set_callbacks(
            on_load=self.on_load_rune_page,
            on_set_default=self.on_set_as_default,
            on_delete=self.on_delete_rune_page,
            on_get_rune_details=self.get_rune_page_details
        )
        
        # Callback to notify other controllers when rune page is loaded
        self.on_rune_page_loaded: Optional[callable] = None
        # Callback to notify when rune page is deleted
        self.on_rune_page_deleted: Optional[callable] = None
        
    def load_champion_rune_pages(self, champion_id: int):
        """Load and display saved rune pages for selected champion"""
        # Clear dropdown first
        self.saved_runes_view.clear_all()
        
        # Load rune pages if champion is selected
        if champion_id:
            rune_pages = self.rune_page_model.get_champion_rune_pages(champion_id)
            self.saved_runes_view.display_rune_pages(rune_pages)
            
            # Don't auto-load default rune page - user should manually select
        
    def load_default_rune_page(self, champion_id: int):
        """Load the default rune page for selected champion"""
        result = self.rune_page_model.get_default_rune_page(champion_id)
        if result:
            data = self.rune_page_model.parse_rune_page_data(result)
            if self.on_rune_page_loaded:
                self.on_rune_page_loaded(data)
                
    def on_load_rune_page(self, page_id: int):
        """Load a specific rune page by ID"""
        result = self.rune_page_model.get_rune_page_by_id(page_id)
        if result:
            data = self.rune_page_model.parse_rune_page_data(result)
            if self.on_rune_page_loaded:
                self.on_rune_page_loaded(data)
                
    def on_set_as_default(self, page_id: int):
        """Set a rune page as the default for the current champion"""
        if not self.rune_state.selected_champion:
            return
            
        self.rune_page_model.set_as_default(page_id, self.rune_state.selected_champion['id'])
        
        # Refresh the display
        self.load_champion_rune_pages(self.rune_state.selected_champion['id'])
        
        # Load the default page into the rune builder
        self.load_default_rune_page(self.rune_state.selected_champion['id'])
        
        # Find and select the default page in the dropdown
        result = self.rune_page_model.get_rune_page_by_id(page_id)
        if result:
            _, name, _, _, _, _, _, _, _ = result  # Unpack all 9 values
            self.select_rune_page_by_name(name)
        
    def on_delete_rune_page(self, page_id: int):
        """Delete a rune page after confirmation"""
        result = messagebox.askyesno("Delete Rune Page", 
                                   "Are you sure you want to delete this rune page?")
        if result:
            self.rune_page_model.delete_rune_page(page_id)
            
            # Refresh the display
            if self.rune_state.selected_champion:
                self.load_champion_rune_pages(self.rune_state.selected_champion['id'])
                
            # Notify that a rune page was deleted
            if self.on_rune_page_deleted:
                self.on_rune_page_deleted()
                
    def get_rune_page_details(self, page_id: int) -> dict:
        """Get detailed rune page data for tooltip display"""
        result = self.rune_page_model.get_rune_page_by_id(page_id)
        if result:
            return self.rune_page_model.parse_rune_page_data(result)
        return {}
    
    def set_rune_page_loaded_callback(self, callback: callable):
        """Set callback for when a rune page is loaded"""
        self.on_rune_page_loaded = callback
        
    def set_rune_page_deleted_callback(self, callback: callable):
        """Set callback for when a rune page is deleted"""
        self.on_rune_page_deleted = callback
        
    def select_rune_page_by_name(self, matchup_name: str):
        """Select a specific rune page in the dropdown by matchup name"""
        # Find the matching rune page and select it
        for page_id, name, primary_tree, secondary_tree, keystone, notes, is_default in getattr(self.saved_runes_view, 'rune_pages_data', []):
            if name == matchup_name:
                # Set the dropdown text to show the selected page
                display_name = f"vs. {name}"
                if bool(is_default):
                    display_name += " (Default)"
                self.saved_runes_view.selected_page.set(display_name)
                
                # Enable buttons and update button text
                self.saved_runes_view.default_btn.configure(state='normal')
                self.saved_runes_view.delete_btn.configure(state='normal')
                self.saved_runes_view._update_default_button_text(bool(is_default))
                break