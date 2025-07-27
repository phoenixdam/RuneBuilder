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
            on_delete=self.on_delete_rune_page
        )
        
        # Callback to notify other controllers when rune page is loaded
        self.on_rune_page_loaded: Optional[callable] = None
        
    def load_champion_rune_pages(self, champion_id: int):
        """Load and display saved rune pages for selected champion"""
        rune_pages = self.rune_page_model.get_champion_rune_pages(champion_id)
        self.saved_runes_view.display_rune_pages(rune_pages)
        
        # Auto-load default rune page if exists
        self.load_default_rune_page(champion_id)
        
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
        
    def on_delete_rune_page(self, page_id: int):
        """Delete a rune page after confirmation"""
        result = messagebox.askyesno("Delete Rune Page", 
                                   "Are you sure you want to delete this rune page?")
        if result:
            self.rune_page_model.delete_rune_page(page_id)
            
            # Refresh the display
            if self.rune_state.selected_champion:
                self.load_champion_rune_pages(self.rune_state.selected_champion['id'])
                
    def set_rune_page_loaded_callback(self, callback: callable):
        """Set callback for when a rune page is loaded"""
        self.on_rune_page_loaded = callback