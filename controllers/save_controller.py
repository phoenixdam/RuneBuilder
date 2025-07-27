import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tkinter import messagebox
from typing import Optional
from models.rune_page_model import RunePageModel
from views.save_panel_view import SavePanelView
from .rune_state import RuneState


class SaveController:
    """Controller for save panel operations"""
    
    def __init__(self, rune_page_model: RunePageModel, save_panel_view: SavePanelView, rune_state: RuneState):
        self.rune_page_model = rune_page_model
        self.save_panel_view = save_panel_view
        self.rune_state = rune_state
        
        # Set up callbacks
        self.save_panel_view.set_callbacks(
            on_save=self.on_save_rune_page,
            on_clear=self.on_clear_all_runes
        )
        
        # Callback to notify when runes are cleared
        self.on_runes_cleared: Optional[callable] = None
        self.on_rune_page_saved: Optional[callable] = None
        
    def on_save_rune_page(self):
        """Save the current rune configuration"""
        # Validate state
        is_valid, error_message = self.rune_state.is_valid_for_saving()
        if not is_valid:
            messagebox.showwarning("Incomplete Build", error_message)
            return
            
        # Validate input
        name = self.save_panel_view.get_rune_page_name()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a rune page name!")
            return
            
        notes = self.save_panel_view.get_notes()
        
        # Prepare rune data
        primary_runes = self.rune_state.get_primary_runes_dict()
        secondary_runes = self.rune_state.get_secondary_runes_dict()
        
        # Save to database
        self.rune_page_model.save_rune_page(
            name=name,
            champion_id=self.rune_state.selected_champion['id'],
            primary_tree=self.rune_state.selected_primary_tree,
            secondary_tree=self.rune_state.selected_secondary_tree,
            keystone=self.rune_state.selected_runes['keystone'],
            primary_runes=primary_runes,
            secondary_runes=secondary_runes,
            stat_shards=self.rune_state.selected_runes['stat_shards'],
            notes=notes,
            is_default=False
        )
        
        messagebox.showinfo("Success", f"Rune page '{name}' saved successfully!")
        
        # Clear the input fields
        self.save_panel_view.clear_inputs()
        
        # Notify that rune page was saved
        if self.on_rune_page_saved:
            self.on_rune_page_saved()
            
    def on_clear_all_runes(self):
        """Clear all selected runes"""
        if self.on_runes_cleared:
            self.on_runes_cleared()
            
    def set_callbacks(self, on_runes_cleared: callable, on_rune_page_saved: callable):
        """Set callbacks for clear and save events"""
        self.on_runes_cleared = on_runes_cleared
        self.on_rune_page_saved = on_rune_page_saved