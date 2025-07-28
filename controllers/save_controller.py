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
            on_clear=self.on_clear_all_runes,
            on_save_new=self.on_save_new_rune_page
        )
        
        # Callback to notify when runes are cleared
        self.on_runes_cleared: Optional[callable] = None
        self.on_rune_page_saved: Optional[callable] = None
        
        # Track current loaded rune page for edit mode
        self.current_rune_page_id: Optional[int] = None
        
    def set_champion_names(self, champion_names):
        """Set champion names for the autocomplete combobox"""
        self.save_panel_view.set_champion_names(champion_names)
        
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
            # Treat empty matchup as "Generic"
            name = "Generic"
        else:
            # Validate that it's a valid champion name
            if not self.save_panel_view.is_valid_matchup():
                messagebox.showwarning("Invalid Matchup", "Please enter a valid champion name for the matchup!")
                return
            
        notes = self.save_panel_view.get_notes()
        
        # Prepare rune data
        primary_runes = self.rune_state.get_primary_runes_dict()
        secondary_runes = self.rune_state.get_secondary_runes_dict()
        
        # Save to database - update if in edit mode, create new otherwise
        if self.current_rune_page_id:
            # Edit mode - update existing rune page
            self.rune_page_model.update_rune_page(
                page_id=self.current_rune_page_id,
                name=name,
                champion_id=self.rune_state.selected_champion['id'],
                primary_tree=self.rune_state.selected_primary_tree,
                secondary_tree=self.rune_state.selected_secondary_tree,
                keystone=self.rune_state.selected_runes['keystone'],
                primary_runes=primary_runes,
                secondary_runes=secondary_runes,
                stat_shards=self.rune_state.selected_runes['stat_shards'],
                notes=notes
            )
            messagebox.showinfo("Success", f"Rune page '{name}' updated successfully!")
        else:
            # Create mode - save new rune page
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
        
        # Don't clear inputs - keep visual state the same
        # Just reset edit mode ID so future saves are treated as new
        self.current_rune_page_id = None
        
        # Notify that rune page was saved
        if self.on_rune_page_saved:
            self.on_rune_page_saved()
            
    def on_save_new_rune_page(self):
        """Save the current rune configuration as a new rune page"""
        # Validate state
        is_valid, error_message = self.rune_state.is_valid_for_saving()
        if not is_valid:
            messagebox.showwarning("Incomplete Build", error_message)
            return
            
        # Validate input
        name = self.save_panel_view.get_rune_page_name()
        if not name:
            # Treat empty matchup as "Generic"
            name = "Generic"
        else:
            # Validate that it's a valid champion name
            if not self.save_panel_view.is_valid_matchup():
                messagebox.showwarning("Invalid Matchup", "Please enter a valid champion name for the matchup!")
                return
            
        notes = self.save_panel_view.get_notes()
        
        # Prepare rune data
        primary_runes = self.rune_state.get_primary_runes_dict()
        secondary_runes = self.rune_state.get_secondary_runes_dict()
        
        # Always save as new (ignore current_rune_page_id)
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
        messagebox.showinfo("Success", f"New rune page '{name}' saved successfully!")
        
        # Don't clear inputs - keep visual state the same
        # Just reset edit mode ID so future saves are treated as new
        self.current_rune_page_id = None
        
        # Notify that rune page was saved
        if self.on_rune_page_saved:
            self.on_rune_page_saved()
            
    def on_clear_all_runes(self):
        """Clear all selected runes"""
        if self.on_runes_cleared:
            self.on_runes_cleared()
            
    def load_rune_page_data_to_panel(self, data: dict):
        """Load rune page data into the save panel for editing"""
        # Set the current rune page ID for edit mode
        self.current_rune_page_id = data.get('id')
        
        # Populate the save panel fields
        self.save_panel_view.matchup_var.set(data.get('name', ''))
        self.save_panel_view.notes_text.delete("1.0", "end")
        self.save_panel_view.notes_text.insert("1.0", data.get('notes', ''))
        
        # Update text color to show valid input
        self.save_panel_view.matchup_entry.configure(fg=self.save_panel_view.matchup_entry.cget('fg'))
        
        # Enable Save New button when a rune page is loaded
        self.save_panel_view.enable_save_new_button()
    
    def clear_edit_mode(self):
        """Clear edit mode and return to create mode"""
        self.current_rune_page_id = None
        self.save_panel_view.clear_inputs()
        # Disable Save New button when not in edit mode
        self.save_panel_view.disable_save_new_button()
    
    def set_callbacks(self, on_runes_cleared: callable, on_rune_page_saved: callable):
        """Set callbacks for clear and save events"""
        self.on_runes_cleared = on_runes_cleared
        self.on_rune_page_saved = on_rune_page_saved