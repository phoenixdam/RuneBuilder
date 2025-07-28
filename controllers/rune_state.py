from typing import Dict, List, Tuple, Optional


class RuneState:
    """Manages the current rune selection state"""
    
    def __init__(self):
        self.selected_champion: Optional[Dict] = None
        self.selected_primary_tree: Optional[str] = None
        self.selected_secondary_tree: Optional[str] = None
        self.selected_runes = {
            'keystone': None,
            'primary_row1': None,
            'primary_row2': None,
            'primary_row3': None,
            'secondary_row1': None,
            'secondary_row2': None,
            'secondary_row3': None,
            'stat_shards': {'offense': None, 'flex': None, 'defense': None}
        }
        
        # Track order of secondary rune selections for FIFO logic
        self.secondary_rune_selection_order: List[Tuple[str, str]] = []
        
        # Track mandatory vs optional rune selections
        self.rune_states = {
            'keystone': {},  # rune_name: 'mandatory' or 'optional'
            'primary_row1': {},
            'primary_row2': {},
            'primary_row3': {},
            'secondary_row1': {},
            'secondary_row2': {},
            'secondary_row3': {},
            'stat_shards': {}
        }
        
    def set_champion(self, champion_id: int, champion_name: str):
        """Set the selected champion or clear selection if None"""
        if champion_id is None or champion_name is None:
            self.selected_champion = None
        else:
            self.selected_champion = {'id': champion_id, 'name': champion_name}
        
    def set_primary_tree(self, tree_name: str):
        """Set the primary tree and clear conflicting selections"""
        # Clear all primary rune selections when changing primary tree
        if self.selected_primary_tree != tree_name:
            self.selected_runes['keystone'] = None
            self.selected_runes['primary_row1'] = None
            self.selected_runes['primary_row2'] = None
            self.selected_runes['primary_row3'] = None
            
            # Clear primary rune states
            self.rune_states['keystone'] = {}
            self.rune_states['primary_row1'] = {}
            self.rune_states['primary_row2'] = {}
            self.rune_states['primary_row3'] = {}
            
        # If this tree is currently selected as secondary, reset secondary selection
        if self.selected_secondary_tree == tree_name:
            self.selected_secondary_tree = None
            # Clear secondary rune selections
            for key in ['secondary_row1', 'secondary_row2', 'secondary_row3']:
                self.selected_runes[key] = None
                self.rune_states[key] = {}
            # Clear secondary rune selection order
            self.secondary_rune_selection_order = []
            
        self.selected_primary_tree = tree_name
        
    def set_secondary_tree(self, tree_name: str):
        """Set the secondary tree and clear previous secondary selections"""
        # Clear previous secondary selections when changing trees
        if self.selected_secondary_tree != tree_name:
            for key in ['secondary_row1', 'secondary_row2', 'secondary_row3']:
                self.selected_runes[key] = None
                self.rune_states[key] = {}
            # Clear secondary rune selection order
            self.secondary_rune_selection_order = []
            
        self.selected_secondary_tree = tree_name
        
    def select_rune(self, rune_type: str, rune_name: str):
        """Select a specific rune with FIFO logic for secondary runes"""
        if rune_type.startswith('secondary_'):
            self._handle_secondary_rune_selection(rune_type, rune_name)
        else:
            self.selected_runes[rune_type] = rune_name
            
    def _handle_secondary_rune_selection(self, row_type: str, rune_name: str):
        """Handle secondary rune selection with FIFO logic"""
        if self._is_rune_already_selected(row_type, rune_name):
            return
        
        if self._is_replacing_same_row_rune(row_type):
            self._remove_old_rune_from_tracking(row_type)
        elif self._should_remove_oldest_rune(row_type):
            self._remove_oldest_selected_rune()
        
        self._select_new_secondary_rune(row_type, rune_name)
        
    def _is_rune_already_selected(self, row_type: str, rune_name: str) -> bool:
        return self.selected_runes[row_type] == rune_name
    
    def _is_replacing_same_row_rune(self, row_type: str) -> bool:
        return self.selected_runes[row_type] is not None
    
    def _remove_old_rune_from_tracking(self, row_type: str):
        old_rune = self.selected_runes[row_type]
        old_selection = (row_type, old_rune)
        if old_selection in self.secondary_rune_selection_order:
            self.secondary_rune_selection_order.remove(old_selection)
    
    def _should_remove_oldest_rune(self, row_type: str) -> bool:
        current_selections = self._get_current_secondary_selections()
        selected_rows = [row for row, _ in current_selections]
        return len(current_selections) >= 2 and row_type not in selected_rows
    
    def _get_current_secondary_selections(self) -> List[Tuple[str, str]]:
        selections = []
        for row_type in ['secondary_row1', 'secondary_row2', 'secondary_row3']:
            if self.selected_runes[row_type]:
                selections.append((row_type, self.selected_runes[row_type]))
        return selections
    
    def _remove_oldest_selected_rune(self):
        if self.secondary_rune_selection_order:
            oldest_row_type, oldest_rune = self.secondary_rune_selection_order.pop(0)
            self.selected_runes[oldest_row_type] = None
    
    def _select_new_secondary_rune(self, row_type: str, rune_name: str):
        self.selected_runes[row_type] = rune_name
        new_selection = (row_type, rune_name)
        if new_selection not in self.secondary_rune_selection_order:
            self.secondary_rune_selection_order.append(new_selection)
            
    def select_stat_shard(self, shard_type: str, shard_name: str):
        """Select a stat shard"""
        self.selected_runes['stat_shards'][shard_type] = shard_name
        
    def load_from_data(self, data: Dict):
        """Load rune state from data dictionary"""
        self.selected_primary_tree = data.get('primary_tree')
        self.selected_secondary_tree = data.get('secondary_tree')
        self.selected_runes['keystone'] = data.get('keystone')
        
        # Load primary runes
        primary_runes = data.get('primary_runes', {})
        for key, value in primary_runes.items():
            self.selected_runes[key] = value
            
        # Load secondary runes
        secondary_runes = data.get('secondary_runes', {})
        for key, value in secondary_runes.items():
            self.selected_runes[key] = value
            
        # Load stat shards
        stat_shards = data.get('stat_shards', {})
        self.selected_runes['stat_shards'] = stat_shards
        
        # Rebuild secondary rune selection order
        self.secondary_rune_selection_order = []
        for row_type in ['secondary_row1', 'secondary_row2', 'secondary_row3']:
            if self.selected_runes[row_type]:
                self.secondary_rune_selection_order.append((row_type, self.selected_runes[row_type]))
                
    def clear_all(self):
        """Clear all rune selections"""
        self.selected_primary_tree = None
        self.selected_secondary_tree = None
        self.selected_runes = {
            'keystone': None,
            'primary_row1': None,
            'primary_row2': None,
            'primary_row3': None,
            'secondary_row1': None,
            'secondary_row2': None,
            'secondary_row3': None,
            'stat_shards': {'offense': None, 'flex': None, 'defense': None}
        }
        self.secondary_rune_selection_order = []
        
        # Clear rune states
        self.rune_states = {
            'keystone': {},
            'primary_row1': {},
            'primary_row2': {},
            'primary_row3': {},
            'secondary_row1': {},
            'secondary_row2': {},
            'secondary_row3': {},
            'stat_shards': {}
        }
        
    def get_primary_runes_dict(self) -> Dict:
        """Get primary runes as dictionary for saving"""
        return {
            'primary_row1': self.selected_runes['primary_row1'],
            'primary_row2': self.selected_runes['primary_row2'],
            'primary_row3': self.selected_runes['primary_row3']
        }
        
    def get_secondary_runes_dict(self) -> Dict:
        """Get secondary runes as dictionary for saving"""
        return {
            'secondary_row1': self.selected_runes['secondary_row1'],
            'secondary_row2': self.selected_runes['secondary_row2'],
            'secondary_row3': self.selected_runes['secondary_row3']
        }
        
    def is_valid_for_saving(self) -> Tuple[bool, str]:
        """Check if current state is valid for saving"""
        if not self.selected_primary_tree:
            return False, "Please select a primary tree first!"
            
        if not self.selected_runes['keystone']:
            return False, "Please select a keystone rune!"
            
        if not self.selected_champion:
            return False, "Please select a champion first!"
            
        return True, ""
        
    def toggle_rune_state(self, rune_type: str, rune_name: str):
        """Toggle a rune between mandatory and optional states"""
        if rune_type not in self.rune_states:
            return
            
        current_state = self.rune_states[rune_type].get(rune_name)
        
        if current_state == 'mandatory':
            # Change from mandatory to optional
            self.rune_states[rune_type][rune_name] = 'optional'
            # Clear from selected runes since it's no longer the active selection
            if self.selected_runes[rune_type] == rune_name:
                self.selected_runes[rune_type] = None
        elif current_state == 'optional':
            # Remove from optional (back to unselected)
            if rune_name in self.rune_states[rune_type]:
                del self.rune_states[rune_type][rune_name]
        else:
            # Not selected, make it optional
            # First, check if there's a mandatory selection in this row and clear it
            if self.selected_runes[rune_type]:
                mandatory_rune = self.selected_runes[rune_type]
                # Clear the mandatory selection
                self.selected_runes[rune_type] = None
                # Remove from states if it exists
                if mandatory_rune in self.rune_states[rune_type]:
                    del self.rune_states[rune_type][mandatory_rune]
            
            # Mark this rune as optional
            self.rune_states[rune_type][rune_name] = 'optional'
        
    def _handle_row_state_changes(self, rune_type: str, rune_name: str):
        """Handle state changes when a rune in a row becomes optional"""
        if rune_type.startswith('secondary_'):
            return  # Secondary runes have different logic
            
        # Find other runes in the same row
        row_runes = self._get_row_runes(rune_type)
        
        # If this rune became optional, clear mandatory state from other runes in the row
        if self.rune_states[rune_type].get(rune_name) == 'optional':
            for other_rune in row_runes:
                if other_rune != rune_name and other_rune in self.rune_states[rune_type]:
                    if self.rune_states[rune_type][other_rune] == 'mandatory':
                        # Change to optional or remove if not selected
                        if self.selected_runes[rune_type] == other_rune:
                            self.rune_states[rune_type][other_rune] = 'optional'
                        else:
                            del self.rune_states[rune_type][other_rune]
                            
    def _get_row_runes(self, rune_type: str) -> List[str]:
        """Get all possible runes for a given rune type's row"""
        # This would need to be populated with actual rune data
        # For now, return empty list as placeholder
        return []
        
    def get_rune_state(self, rune_type: str, rune_name: str) -> str:
        """Get the state of a rune (mandatory, optional, or unselected)"""
        if self.selected_runes[rune_type] == rune_name:
            return self.rune_states[rune_type].get(rune_name, 'mandatory')
        elif rune_name in self.rune_states[rune_type]:
            return self.rune_states[rune_type][rune_name]
        else:
            return 'unselected'