import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Dict, List, Set, Tuple, Optional
from models.rune_data_model import RuneDataModel
from views.rune_view import RuneView
from .rune_state import RuneState


class RuneController:
    """Controller for rune selection and state management"""
    
    def __init__(self, rune_data_model: RuneDataModel, rune_view: RuneView, rune_state: RuneState):
        self.rune_data_model = rune_data_model
        self.rune_view = rune_view
        self.rune_state = rune_state
        
        # Set rune data model in view for tooltips
        self.rune_view.set_rune_data_model(rune_data_model)
        
        # Set up callbacks
        self.rune_view.set_callbacks(
            on_tree_select=self.on_primary_tree_selected,
            on_secondary_tree_select=self.on_secondary_tree_selected,
            on_rune_select=self.on_rune_selected,
            on_stat_shard_select=self.on_stat_shard_selected,
            on_rune_right_click=self.on_rune_right_click
        )
        
    def initialize(self):
        """Initialize rune interface"""
        # Create tree buttons
        self.rune_view.create_tree_buttons(self.rune_data_model.rune_trees)
        
        # Create stat shards
        self.rune_view.create_stat_shards(self.rune_data_model.stat_shards)
        
        # Update secondary tree options
        self.update_secondary_tree_options()
        
        # Schedule preloading in background to not block startup
        self._schedule_preloading()
        
    def on_primary_tree_selected(self, tree_name: str):
        """Handle primary tree selection"""
        # Don't do anything if tree is already selected
        if self.rune_state.selected_primary_tree == tree_name:
            return
            
        self.rune_state.set_primary_tree(tree_name)
        
        # Auto-select secondary tree (next available tree)
        self._auto_select_secondary_tree(tree_name)
        
        self.update_tree_selection_visual()
        self.display_primary_runes()
        self.update_secondary_tree_options()
        self.display_secondary_runes()
        
        # Update visuals to reflect cleared selections
        self.update_all_rune_visuals()
        
    def _auto_select_secondary_tree(self, primary_tree: str):
        """Auto-select the next available secondary tree"""
        all_trees = self.rune_data_model.get_tree_names()
        
        # Find index of primary tree
        try:
            primary_index = all_trees.index(primary_tree)
        except ValueError:
            return
            
        # Select the next tree, wrapping around if needed
        next_index = (primary_index + 1) % len(all_trees)
        secondary_tree = all_trees[next_index]
        
        # Set secondary tree in state
        self.rune_state.set_secondary_tree(secondary_tree)
        
    def on_secondary_tree_selected(self, tree_name: str):
        """Handle secondary tree selection"""
        # Don't do anything if tree is already selected
        if self.rune_state.selected_secondary_tree == tree_name:
            return
            
        self.rune_state.set_secondary_tree(tree_name)
        self.display_secondary_runes()
        
        # Update visuals to reflect cleared secondary selections
        self.update_all_rune_visuals()
        
    def on_rune_selected(self, rune_type: str, rune_name: str):
        """Handle rune selection"""
        if rune_type.startswith('secondary_'):
            # Special logic for secondary runes
            self._handle_secondary_mandatory_selection(rune_type, rune_name)
        else:
            # Primary rune logic - clear ALL rune states in this row when making a mandatory selection
            if rune_type in self.rune_state.rune_states:
                self.rune_state.rune_states[rune_type].clear()
            
            self.rune_state.select_rune(rune_type, rune_name)
            
            # Mark as mandatory by default when selected via left-click
            if rune_type in self.rune_state.rune_states:
                self.rune_state.rune_states[rune_type][rune_name] = 'mandatory'
        
        # Update visual feedback
        if rune_type.startswith('secondary_'):
            self.update_all_secondary_rune_visuals()
        else:
            self.update_rune_selection_visual(rune_type, rune_name)
            
    def on_rune_right_click(self, rune_type: str, rune_name: str):
        """Handle rune right-click for state toggling"""
        if rune_type.startswith('secondary_'):
            # Special logic for secondary runes
            self._handle_secondary_right_click(rune_type, rune_name)
        else:
            # Primary rune logic
            self.rune_state.toggle_rune_state(rune_type, rune_name)
        
        # Update visual feedback for entire interface to reflect state changes
        self.update_all_rune_visuals()
        
    def _handle_secondary_mandatory_selection(self, rune_type: str, rune_name: str):
        """Handle secondary rune mandatory selection with FIFO logic"""
        # Check if there's already a mandatory rune in this row
        current_mandatory_in_row = None
        for rune, state in self.rune_state.rune_states[rune_type].items():
            if state == 'mandatory':
                current_mandatory_in_row = rune
                break
        
        if current_mandatory_in_row:
            # Clear the existing mandatory rune in this row
            del self.rune_state.rune_states[rune_type][current_mandatory_in_row]
            # Remove from selected runes tracking if it was there
            if self.rune_state.selected_runes[rune_type] == current_mandatory_in_row:
                self.rune_state.selected_runes[rune_type] = None
            # Remove from FIFO order
            old_selection = (rune_type, current_mandatory_in_row)
            if old_selection in self.rune_state.secondary_rune_selection_order:
                self.rune_state.secondary_rune_selection_order.remove(old_selection)
        else:
            # No mandatory rune in this row, check if we have 2 mandatory runes already
            mandatory_count = 0
            secondary_types = ['secondary_row1', 'secondary_row2', 'secondary_row3']
            
            for sec_type in secondary_types:
                for rune, state in self.rune_state.rune_states[sec_type].items():
                    if state == 'mandatory':
                        mandatory_count += 1
            
            if mandatory_count >= 2:
                # Remove the oldest mandatory rune (FIFO)
                self._remove_oldest_mandatory_secondary_rune()
        
        # Clear optional states in this row
        runes_to_remove = []
        for rune, state in self.rune_state.rune_states[rune_type].items():
            if state == 'optional':
                runes_to_remove.append(rune)
        for rune in runes_to_remove:
            del self.rune_state.rune_states[rune_type][rune]
        
        # Select the rune and mark as mandatory
        self.rune_state.select_rune(rune_type, rune_name)
        self.rune_state.rune_states[rune_type][rune_name] = 'mandatory'
        
    def _remove_oldest_mandatory_secondary_rune(self):
        """Remove the oldest mandatory secondary rune using FIFO logic"""
        secondary_types = ['secondary_row1', 'secondary_row2', 'secondary_row3']
        
        # Find the oldest mandatory rune by checking the selection order
        for selection in self.rune_state.secondary_rune_selection_order:
            row_type, rune_name = selection
            if (row_type in secondary_types and 
                row_type in self.rune_state.rune_states and
                self.rune_state.rune_states[row_type].get(rune_name) == 'mandatory'):
                
                # Remove this mandatory rune
                del self.rune_state.rune_states[row_type][rune_name]
                # Remove from selected runes
                if self.rune_state.selected_runes[row_type] == rune_name:
                    self.rune_state.selected_runes[row_type] = None
                # Remove from selection order
                self.rune_state.secondary_rune_selection_order.remove(selection)
                break
                
    def _handle_secondary_right_click(self, rune_type: str, rune_name: str):
        """Handle secondary rune right-click with special logic"""
        current_state = self.rune_state.rune_states[rune_type].get(rune_name)
        
        if current_state == 'mandatory':
            # Change from mandatory to optional
            self.rune_state.rune_states[rune_type][rune_name] = 'optional'
            # Clear from selected runes since it's no longer the active selection
            if self.rune_state.selected_runes[rune_type] == rune_name:
                self.rune_state.selected_runes[rune_type] = None
            # Remove from FIFO order
            old_selection = (rune_type, rune_name)
            if old_selection in self.rune_state.secondary_rune_selection_order:
                self.rune_state.secondary_rune_selection_order.remove(old_selection)
        elif current_state == 'optional':
            # Remove from optional (back to unselected)
            if rune_name in self.rune_state.rune_states[rune_type]:
                del self.rune_state.rune_states[rune_type][rune_name]
        else:
            # Not selected, make it optional
            # Check if there's a mandatory selection in this row and clear it
            current_mandatory_in_row = None
            for rune, state in self.rune_state.rune_states[rune_type].items():
                if state == 'mandatory':
                    current_mandatory_in_row = rune
                    break
            
            if current_mandatory_in_row:
                # Clear the mandatory selection in this row
                del self.rune_state.rune_states[rune_type][current_mandatory_in_row]
                if self.rune_state.selected_runes[rune_type] == current_mandatory_in_row:
                    self.rune_state.selected_runes[rune_type] = None
                # Remove from FIFO order
                old_selection = (rune_type, current_mandatory_in_row)
                if old_selection in self.rune_state.secondary_rune_selection_order:
                    self.rune_state.secondary_rune_selection_order.remove(old_selection)
            
            # Mark this rune as optional
            self.rune_state.rune_states[rune_type][rune_name] = 'optional'
            
    def on_stat_shard_selected(self, shard_type: str, shard_name: str):
        """Handle stat shard selection"""
        self.rune_state.select_stat_shard(shard_type, shard_name)
        
        # Update visual feedback
        selected_items = {(shard_type, shard_name)}
        self.rune_view.update_button_visuals(self.rune_view.stat_buttons, selected_items, [shard_type])
        
    def update_tree_selection_visual(self):
        """Update visual feedback for tree selection"""
        tree_colors = {name: data['color'] for name, data in self.rune_data_model.rune_trees.items()}
        self.rune_view.update_tree_selection_visual(self.rune_state.selected_primary_tree, tree_colors)
        
    def display_primary_runes(self):
        """Display runes for selected primary tree"""
        self.rune_view.display_primary_runes(self.rune_state.selected_primary_tree)
        
    def update_secondary_tree_options(self):
        """Update secondary tree selection options"""
        all_trees = self.rune_data_model.get_tree_names()
        tree_colors = {name: data['color'] for name, data in self.rune_data_model.rune_trees.items()}
        self.rune_view.update_secondary_tree_options(all_trees, self.rune_state.selected_primary_tree, tree_colors)
        
    def display_secondary_runes(self):
        """Display secondary tree runes"""
        self.rune_view.display_secondary_runes(self.rune_state.selected_secondary_tree)
        
    def update_all_secondary_rune_visuals(self):
        """Update visual feedback for all secondary runes"""
        secondary_filter = ['secondary_row1', 'secondary_row2', 'secondary_row3']
        selected_items = {(row_type, self.rune_state.selected_runes[row_type]) for row_type in secondary_filter 
                         if self.rune_state.selected_runes[row_type]}
        self.rune_view.update_button_visuals(self.rune_view.rune_buttons, selected_items, secondary_filter, self.rune_state.rune_states)
        
    def update_rune_selection_visual(self, rune_type: str, selected_rune: str):
        """Update visual feedback for rune selection"""
        selected_items = {(rune_type, selected_rune)}
        self.rune_view.update_button_visuals(self.rune_view.rune_buttons, selected_items, [rune_type], self.rune_state.rune_states)
        
    def update_all_rune_visuals(self):
        """Update visual feedback for all selected runes"""
        # Update primary tree visual
        if self.rune_state.selected_primary_tree:
            self.update_tree_selection_visual()
        
        # Collect all selected runes
        selected_runes = {(rune_type, rune_name) for rune_type, rune_name in self.rune_state.selected_runes.items() 
                         if rune_name and rune_type != 'stat_shards'}
        self.rune_view.update_button_visuals(self.rune_view.rune_buttons, selected_runes, None, self.rune_state.rune_states)
        
        # Collect all selected stat shards
        selected_shards = {(shard_type, shard_name) for shard_type, shard_name in self.rune_state.selected_runes['stat_shards'].items() 
                          if shard_name}
        self.rune_view.update_button_visuals(self.rune_view.stat_buttons, selected_shards)
        
    def load_rune_page_data(self, data: Dict):
        """Load rune page data into state and update visuals"""
        self.rune_state.load_from_data(data)
        
        # Update UI
        self.update_tree_selection_visual()
        self.display_primary_runes()
        self.update_secondary_tree_options()
        self.display_secondary_runes()
        self.update_all_rune_visuals()
        
    def clear_all_runes(self):
        """Clear all selected runes"""
        self.rune_state.clear_all()
        self.rune_view.clear_all_runes()
        
        # Reset tree visual selection to show no selection with proper colors
        tree_colors = {name: data['color'] for name, data in self.rune_data_model.rune_trees.items()}
        self.rune_view.update_tree_selection_visual(None, tree_colors)
        
        # Update secondary tree options to show all available trees (no primary tree selected)
        all_trees = self.rune_data_model.get_tree_names()
        tree_colors = {name: data['color'] for name, data in self.rune_data_model.rune_trees.items()}
        self.rune_view.update_secondary_tree_options(all_trees, None, tree_colors)
        
    def _schedule_preloading(self):
        """Schedule rune widget preloading to run after startup"""
        # Disable preloading completely for now to avoid any startup interference
        pass