import tkinter as tk
from typing import Dict, List, Callable, Optional, Tuple
from views.ui_constants import UIConstants
from views.image_loader import ImageLoader


class RuneView:
    """View component for rune selection interface"""
    
    def __init__(self, parent: tk.Widget, image_loader: ImageLoader):
        self.parent = parent
        self.image_loader = image_loader
        self.rune_data_model = None  # Will be set by controller
        self.tree_buttons: Dict[str, tk.Button] = {}
        self.rune_buttons: Dict[Tuple, tk.Button] = {}
        self.stat_buttons: Dict[Tuple, tk.Button] = {}
        self.cached_rune_buttons: Dict[str, Dict] = {}
        self.primary_tree_widgets: Dict[str, tk.Widget] = {}
        self.secondary_tree_widgets: Dict[str, tk.Widget] = {}
        self._tooltips_enabled = True  # Performance control flag
        
        # Callbacks
        self.on_tree_select: Optional[Callable] = None
        self.on_secondary_tree_select: Optional[Callable] = None
        self.on_rune_select: Optional[Callable] = None
        self.on_rune_right_click: Optional[Callable] = None
        self.on_stat_shard_select: Optional[Callable] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup main rune selection area"""
        rune_frame = tk.Frame(self.parent, bg=UIConstants.BACKGROUND_COLOR)
        rune_frame.pack(fill='both', expand=True)
        
        # Main content container
        content_frame = tk.Frame(rune_frame, bg=UIConstants.BACKGROUND_COLOR)
        content_frame.pack(fill='both', expand=True, padx=8, pady=4)
        
        # Two-column layout
        columns_frame = tk.Frame(content_frame, bg=UIConstants.BACKGROUND_COLOR)
        columns_frame.pack(fill='both', expand=True)
        
        # Left column - Primary
        self._setup_primary_column(columns_frame)
        
        # Right column - Secondary
        self._setup_secondary_column(columns_frame)
        
    def _setup_primary_column(self, parent: tk.Widget):
        """Setup primary rune selection column"""
        primary_column = tk.Frame(parent, bg=UIConstants.BACKGROUND_COLOR)
        primary_column.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        # Primary header
        primary_header = tk.Frame(primary_column, bg=UIConstants.BACKGROUND_COLOR)
        primary_header.pack(fill='x', pady=(0, 8))
        
        primary_label = tk.Label(primary_header, text="PRIMARY", 
                                font=('Arial', 11, 'bold'), fg=UIConstants.TEXT_COLOR,
                                bg=UIConstants.BACKGROUND_COLOR)
        primary_label.pack()
        
        # Primary tree selection
        self.primary_tree_frame = tk.Frame(primary_column, bg=UIConstants.BACKGROUND_COLOR)
        self.primary_tree_frame.pack(fill='x', pady=(0, 12))
        
        # Primary runes container
        self.primary_runes_frame = tk.Frame(primary_column, bg=UIConstants.BACKGROUND_COLOR)
        self.primary_runes_frame.pack(fill='both', expand=True)
        
    def _setup_secondary_column(self, parent: tk.Widget):
        """Setup secondary rune selection column"""
        secondary_column = tk.Frame(parent, bg=UIConstants.BACKGROUND_COLOR)
        secondary_column.pack(side='right', fill='both', expand=True, padx=(8, 0))
        
        # Secondary header
        secondary_header = tk.Frame(secondary_column, bg=UIConstants.BACKGROUND_COLOR)
        secondary_header.pack(fill='x', pady=(0, 8))
        
        secondary_label = tk.Label(secondary_header, text="SECONDARY", 
                                  font=('Arial', 11, 'bold'), fg=UIConstants.TEXT_COLOR,
                                  bg=UIConstants.BACKGROUND_COLOR)
        secondary_label.pack()
        
        # Secondary tree selection
        self.secondary_tree_frame = tk.Frame(secondary_column, bg=UIConstants.BACKGROUND_COLOR)
        self.secondary_tree_frame.pack(pady=(0, 12))
        
        # Secondary runes container
        self.secondary_runes_frame = tk.Frame(secondary_column, bg=UIConstants.BACKGROUND_COLOR)
        self.secondary_runes_frame.pack(fill='x', pady=(0, 12))
        
        # Stat shards section
        shards_header = tk.Frame(secondary_column, bg=UIConstants.BACKGROUND_COLOR)
        shards_header.pack(fill='x', pady=(0, 8))
        
        stats_label = tk.Label(shards_header, text="SHARDS", 
                              font=('Arial', 11, 'bold'), fg=UIConstants.TEXT_COLOR,
                              bg=UIConstants.BACKGROUND_COLOR)
        stats_label.pack()
        
        # Shards container
        self.stats_frame = tk.Frame(secondary_column, bg=UIConstants.BACKGROUND_COLOR)
        self.stats_frame.pack(fill='x')
        
    def set_callbacks(self, on_tree_select: Callable, on_secondary_tree_select: Callable,
                     on_rune_select: Callable, on_stat_shard_select: Callable, 
                     on_rune_right_click: Callable = None):
        """Set callbacks for rune selection events"""
        self.on_tree_select = on_tree_select
        self.on_secondary_tree_select = on_secondary_tree_select
        self.on_rune_select = on_rune_select
        self.on_stat_shard_select = on_stat_shard_select
        self.on_rune_right_click = on_rune_right_click
        
    def set_rune_data_model(self, rune_data_model):
        """Set the rune data model for accessing descriptions"""
        self.rune_data_model = rune_data_model
        
    def create_tree_buttons(self, rune_trees: Dict):
        """Create rune tree selection buttons"""
        tree_frame = tk.Frame(self.primary_tree_frame, bg=UIConstants.BACKGROUND_COLOR)
        tree_frame.pack()
        
        for i, (tree_name, tree_data) in enumerate(rune_trees.items()):
            tree_icon = self.image_loader.load_tree_icon(tree_name, tree_data['color'], size=UIConstants.TREE_ICON_SIZE)
            
            btn = tk.Button(tree_frame, image=tree_icon, text=tree_name, 
                           font=('Arial', UIConstants.FONT_SIZE_TREE_BUTTON, 'bold'), compound='top',
                           bg=tree_data['color'], fg=UIConstants.BUTTON_SELECTED_FG,
                           width=UIConstants.TREE_BUTTON_SIZE[0], 
                           height=UIConstants.TREE_BUTTON_SIZE[1], 
                           wraplength=UIConstants.TREE_BUTTON_WRAP_LENGTH,
                           command=lambda t=tree_name: self._on_tree_clicked(t))
            btn.image = tree_icon
            btn.grid(row=0, column=i, padx=UIConstants.TREE_BUTTON_PADDING)
            self.tree_buttons[tree_name] = btn
            
    def _on_tree_clicked(self, tree_name: str):
        """Handle tree button click"""
        if self.on_tree_select:
            self.on_tree_select(tree_name)
            
    def create_stat_shards(self, stat_shards: Dict):
        """Create stat shard selection interface"""
        shard_types = ['offense', 'flex', 'defense']
        
        for i, shard_type in enumerate(shard_types):
            shard_frame = tk.Frame(self.stats_frame, bg=UIConstants.BACKGROUND_COLOR)
            shard_frame.grid(row=i, column=0, pady=(0, 3))
            self.stats_frame.grid_columnconfigure(0, weight=1)
            
            for j, shard in enumerate(stat_shards[shard_type]):
                shard_image = self.image_loader.load_stat_shard_image(shard, size=(20, 20))
                config = {'width': 25, 'height': 25}
                btn = self._create_rune_button(shard_frame, shard, shard_image, config,
                                             lambda st=shard_type, s=shard: self._on_stat_shard_clicked(st, s))
                btn.grid(row=0, column=j, padx=1)
                self.stat_buttons[(shard_type, shard)] = btn
                
    def _on_stat_shard_clicked(self, shard_type: str, shard_name: str):
        """Handle stat shard click"""
        if self.on_stat_shard_select:
            self.on_stat_shard_select(shard_type, shard_name)
            
    def preload_rune_widgets(self, rune_trees: Dict):
        """Pre-create all rune tree widgets to eliminate flickering"""
        for tree_name in rune_trees.keys():
            primary_widget = tk.Frame(self.primary_runes_frame, bg=UIConstants.BACKGROUND_COLOR)
            self._build_primary_tree_content(primary_widget, tree_name, rune_trees[tree_name])
            self.primary_tree_widgets[tree_name] = primary_widget
            
            secondary_widget = tk.Frame(self.secondary_runes_frame, bg=UIConstants.BACKGROUND_COLOR)
            self._build_secondary_tree_content(secondary_widget, tree_name, rune_trees[tree_name])
            self.secondary_tree_widgets[tree_name] = secondary_widget
            
    def _build_primary_tree_content(self, parent_widget: tk.Widget, tree_name: str, tree_data: Dict):
        """Build primary tree content in the specified widget"""
        tree_buttons = {}
        
        # Keystones
        keystone_label = tk.Label(parent_widget, text="KEYSTONES",
                                 font=('Arial', 12, 'bold'), fg=tree_data['color'],
                                 bg=UIConstants.BACKGROUND_COLOR)
        keystone_label.pack(pady=(0, 10))
        
        keystone_frame = tk.Frame(parent_widget, bg=UIConstants.BACKGROUND_COLOR)
        keystone_frame.pack(pady=(0, 20))
        
        for i, keystone in enumerate(tree_data['keystones']):
            rune_image = self.image_loader.load_rune_image(keystone, size=(48, 48))
            config = {'width': 55, 'height': 55}
            btn = self._create_rune_button(keystone_frame, keystone, rune_image, config,
                                         lambda k=keystone: self._on_rune_clicked('keystone', k), 'keystone')
            btn.grid(row=0, column=i, padx=3, pady=1)
            tree_buttons[('keystone', keystone)] = btn
        
        # Other rows
        rows = ['row1', 'row2', 'row3']
        for row in rows:
            row_frame = tk.Frame(parent_widget, bg=UIConstants.BACKGROUND_COLOR)
            row_frame.pack(pady=(5, 5))
            
            for j, rune in enumerate(tree_data[row]):
                rune_image = self.image_loader.load_rune_image(rune, size=(32, 32))
                config = {'width': 40, 'height': 40}
                btn = self._create_rune_button(row_frame, rune, rune_image, config,
                                             lambda r=f'primary_{row}', rn=rune: self._on_rune_clicked(r, rn), f'primary_{row}')
                btn.grid(row=0, column=j, padx=2)
                tree_buttons[(f'primary_{row}', rune)] = btn
        
        self.cached_rune_buttons[f'primary_{tree_name}'] = tree_buttons
        
    def _build_secondary_tree_content(self, parent_widget: tk.Widget, tree_name: str, tree_data: Dict):
        """Build secondary tree content in the specified widget"""
        tree_buttons = {}
        
        # Secondary tree label
        label = tk.Label(parent_widget, text=tree_name,
                        font=('Arial', 12, 'bold'), fg=tree_data['color'],
                        bg=UIConstants.BACKGROUND_COLOR)
        label.pack(pady=(0, 10))
        
        # Only show rows 1-3 for secondary tree
        rows = ['row1', 'row2', 'row3']
        for row in rows:
            row_frame = tk.Frame(parent_widget, bg=UIConstants.BACKGROUND_COLOR)
            row_frame.pack(pady=5)
            
            for j, rune in enumerate(tree_data[row]):
                rune_image = self.image_loader.load_rune_image(rune, size=(28, 28))
                config = {'width': 35, 'height': 35}
                btn = self._create_rune_button(row_frame, rune, rune_image, config,
                                             lambda r=f'secondary_{row}', rn=rune: self._on_rune_clicked(r, rn), f'secondary_{row}')
                btn.grid(row=0, column=j, padx=1)
                tree_buttons[(f'secondary_{row}', rune)] = btn
        
        self.cached_rune_buttons[f'secondary_{tree_name}'] = tree_buttons
        
    def _create_rune_button(self, parent: tk.Widget, item_name: str, image, button_config: Dict, command: Callable, rune_type: str = None) -> tk.Button:
        """Helper method to create rune buttons with consistent styling"""
        btn = tk.Button(parent, image=image,
                       width=button_config.get('width', 100), 
                       height=button_config.get('height', 60), 
                       bg=UIConstants.BUTTON_DEFAULT_BG, fg=UIConstants.BUTTON_DEFAULT_FG, 
                       relief='raised', command=command)
        btn.image = image
        
        # Add right-click binding for rune state toggling
        if self.on_rune_right_click and rune_type:
            btn.bind("<Button-3>", lambda e: self._on_rune_right_click(rune_type, item_name))
        
        # Add tooltip with rune description
        if self.rune_data_model:
            description = self.rune_data_model.get_rune_description(item_name)
            self._create_rune_tooltip(btn, item_name, description)
        
        return btn
        
    def _create_rune_tooltip(self, widget: tk.Widget, rune_name: str, description: str):
        """Create a tooltip for a rune widget with performance optimizations"""
        def on_enter(event):
            # Skip if tooltips are disabled for performance
            if not getattr(self, '_tooltips_enabled', True):
                return
                
            # Cancel any pending tooltip operations
            if hasattr(widget, 'tooltip_timer') and widget.tooltip_timer:
                widget.master.after_cancel(widget.tooltip_timer)
                
            cleanup_tooltip()
            
            # Delay tooltip creation to prevent rapid showing/hiding
            widget.tooltip_timer = widget.master.after(500, lambda: show_tooltip(event))
            
        def show_tooltip(event):
            try:
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                tooltip.configure(bg=UIConstants.TOOLTIP_BG)
                
                # Title
                title_label = tk.Label(tooltip, text=rune_name, 
                                     font=('Arial', 11, 'bold'), 
                                     fg=UIConstants.BACKGROUND_COLOR, 
                                     bg=UIConstants.TOOLTIP_BG)
                title_label.pack(padx=5, pady=(5, 0))
                
                # Description
                desc_label = tk.Label(tooltip, text=description, 
                                    font=('Arial', 10), 
                                    fg=UIConstants.BACKGROUND_COLOR, 
                                    bg=UIConstants.TOOLTIP_BG,
                                    wraplength=300, justify='left')
                desc_label.pack(padx=5, pady=(0, 5))
                
                widget.tooltip = tooltip
                widget.tooltip_timer = None
            except:
                pass
            
        def cleanup_tooltip():
            # Cancel timer if exists
            if hasattr(widget, 'tooltip_timer') and widget.tooltip_timer:
                widget.master.after_cancel(widget.tooltip_timer)
                widget.tooltip_timer = None
                
            if hasattr(widget, 'tooltip') and widget.tooltip:
                try:
                    widget.tooltip.destroy()
                except:
                    pass
                widget.tooltip = None
                
        def on_leave(event):
            cleanup_tooltip()
                
        # Initialize tooltip attributes
        widget.tooltip = None
        widget.tooltip_timer = None
        
        # Bind events
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", lambda e: cleanup_tooltip())
        widget.bind("<FocusOut>", lambda e: cleanup_tooltip())
        
    def _on_rune_right_click(self, rune_type: str, rune_name: str):
        """Handle rune right-click for state toggling"""
        if self.on_rune_right_click:
            self.on_rune_right_click(rune_type, rune_name)
        
    def _on_rune_clicked(self, rune_type: str, rune_name: str):
        """Handle rune button click"""
        if self.on_rune_select:
            self.on_rune_select(rune_type, rune_name)
            
    def update_tree_selection_visual(self, selected_primary_tree: str, tree_colors: Dict):
        """Update visual feedback for tree selection"""
        for name, btn in self.tree_buttons.items():
            tree_color = tree_colors.get(name, '#3C3C41')
            if name == selected_primary_tree:
                btn.configure(relief='sunken', bg=tree_color, bd=2)
            else:
                btn.configure(relief='raised', bg=tree_color, bd=2)
                
    def display_primary_runes(self, tree_name: str):
        """Display runes for selected primary tree using cached widgets"""
        # Hide all primary tree widgets
        for widget in self.primary_tree_widgets.values():
            widget.pack_forget()
        
        # Clear old button references
        self.rune_buttons = {k: v for k, v in self.rune_buttons.items() 
                            if not k[0].startswith(('keystone', 'primary_'))}
        
        if not tree_name:
            return
        
        # Show the cached widget for selected tree
        widget = self.primary_tree_widgets[tree_name]
        widget.pack(fill='both', expand=True)
        
        # Restore button references for this tree
        tree_buttons = self.cached_rune_buttons[f'primary_{tree_name}']
        self.rune_buttons.update(tree_buttons)
        
    def update_secondary_tree_options(self, all_trees: List[str], selected_primary_tree: str, tree_colors: Dict):
        """Update secondary tree selection options"""
        # Clear existing secondary tree buttons
        for widget in self.secondary_tree_frame.winfo_children():
            widget.destroy()
        
        # Filter out the primary tree from available secondary trees
        available_trees = [tree for tree in all_trees if tree != selected_primary_tree]
        
        for i, tree_name in enumerate(available_trees):
            btn = tk.Button(self.secondary_tree_frame, text=tree_name,
                           font=('Arial', 9, 'bold'), wraplength=70,
                           width=10, height=2,
                           bg=tree_colors[tree_name], fg=UIConstants.BUTTON_SELECTED_FG,
                           command=lambda t=tree_name: self._on_secondary_tree_clicked(t))
            
            btn.grid(row=0, column=i, padx=2, pady=2)
            
    def _on_secondary_tree_clicked(self, tree_name: str):
        """Handle secondary tree button click"""
        if self.on_secondary_tree_select:
            self.on_secondary_tree_select(tree_name)
            
    def display_secondary_runes(self, tree_name: str):
        """Display secondary tree runes using cached widgets"""
        # Hide all secondary tree widgets
        for widget in self.secondary_tree_widgets.values():
            widget.pack_forget()
        
        # Clear old button references
        self.rune_buttons = {k: v for k, v in self.rune_buttons.items() 
                            if not k[0].startswith('secondary_')}
        
        if not tree_name:
            return
        
        # Show the cached widget for selected tree
        widget = self.secondary_tree_widgets[tree_name]
        widget.pack(fill='x', pady=(0, 12))
        
        # Restore button references for this tree
        tree_buttons = self.cached_rune_buttons[f'secondary_{tree_name}']
        self.rune_buttons.update(tree_buttons)
        
    def update_button_visuals(self, button_dict: Dict, selected_items: set, category_filter: List = None, rune_states: Dict = None):
        """Update button visuals with reset-then-highlight pattern (optimized)"""
        # Batch updates to prevent excessive redraws
        updates = []
        
        # Reset all buttons to default state
        for key, btn in button_dict.items():
            if category_filter is None or key[0] in category_filter:
                updates.append((btn, UIConstants.BUTTON_DEFAULT_BG, UIConstants.BUTTON_DEFAULT_FG, 'raised'))
        
        # Highlight selected items and optional items based on their state
        for key, btn in button_dict.items():
            if category_filter is None or key[0] in category_filter:
                rune_type, rune_name = key
                
                # Check rune states first to handle optional runes
                if rune_states and rune_type in rune_states:
                    state = rune_states[rune_type].get(rune_name)
                    if state == 'optional':
                        # Override the default update for this button
                        updates = [(b, bg, fg, relief) for (b, bg, fg, relief) in updates if b != btn]
                        updates.append((btn, UIConstants.BUTTON_OPTIONAL_BG, UIConstants.BUTTON_OPTIONAL_FG, 'sunken'))
                    elif state == 'mandatory' or key in selected_items:
                        # Override the default update for this button
                        updates = [(b, bg, fg, relief) for (b, bg, fg, relief) in updates if b != btn]
                        updates.append((btn, UIConstants.BUTTON_SELECTED_BG, UIConstants.BUTTON_SELECTED_FG, 'sunken'))
                elif key in selected_items:
                    # Override the default update for this button
                    updates = [(b, bg, fg, relief) for (b, bg, fg, relief) in updates if b != btn]
                    updates.append((btn, UIConstants.BUTTON_SELECTED_BG, UIConstants.BUTTON_SELECTED_FG, 'sunken'))
        
        # Apply all updates at once
        for btn, bg, fg, relief in updates:
            try:
                current_bg = btn.cget('bg')
                current_fg = btn.cget('fg')
                current_relief = btn.cget('relief')
                
                # Only update if values actually changed
                if current_bg != bg or current_fg != fg or current_relief != relief:
                    btn.configure(bg=bg, fg=fg, relief=relief)
            except:
                pass  # Widget might be destroyed
                                 
    def clear_all_runes(self):
        """Clear all rune selections visually"""
        # Clear UI
        for widget in self.primary_runes_frame.winfo_children():
            widget.destroy()
        for widget in self.secondary_runes_frame.winfo_children():
            widget.destroy()
        
        # Reset tree button styles
        for btn in self.tree_buttons.values():
            btn.configure(relief='raised', bd=1)
        
        # Reset button styles
        try:
            for btn in self.rune_buttons.values():
                btn.configure(bg=UIConstants.BUTTON_DEFAULT_BG, fg=UIConstants.BUTTON_DEFAULT_FG, relief='raised')
        except:
            pass
        
        try:
            for btn in self.stat_buttons.values():
                btn.configure(bg=UIConstants.BUTTON_DEFAULT_BG, fg=UIConstants.BUTTON_DEFAULT_FG, relief='raised')
        except:
            pass
        
        # Clear button dictionaries
        self.rune_buttons.clear()