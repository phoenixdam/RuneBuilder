import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Callable, Dict, Optional
from views.ui_constants import UIConstants
from views.image_loader import ImageLoader
import random


class ChampionView:
    """View component for champion selection panel"""
    
    def __init__(self, parent: tk.Widget, image_loader: ImageLoader):
        self.parent = parent
        self.image_loader = image_loader
        self.champion_buttons: Dict[int, tk.Button] = {}
        self.profile_buttons: Dict[int, tk.Button] = {}
        self.last_selected_champion: Optional[int] = None
        self.current_filter_profile_id: Optional[int] = None
        self.on_champion_select: Optional[Callable] = None
        self.on_create_profile: Optional[Callable] = None
        self.on_edit_profile: Optional[Callable] = None
        self.on_filter_by_profile: Optional[Callable] = None
        self.on_get_champion_matchups: Optional[Callable] = None
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup champion selection panel UI as horizontal row"""
        self.champion_frame = tk.Frame(self.parent, bg=UIConstants.BACKGROUND_COLOR)
        self.champion_frame.pack(fill='x')
        
        # Search box and toolbar at the top
        search_container = tk.Frame(self.champion_frame, bg=UIConstants.BACKGROUND_COLOR)
        search_container.pack(fill='x', pady=(0, 5))
        
        # Search entry on the left - match saved runes dropdown height exactly
        self.search_var = tk.StringVar()
        
        # Create a wrapper frame to control the exact height and width to match dropdown
        search_wrapper = tk.Frame(search_container, bg=UIConstants.BACKGROUND_COLOR, height=28, width=235)
        search_wrapper.pack(side='left')
        search_wrapper.pack_propagate(False)  # Prevent frame from shrinking
        
        self.search_entry = tk.Entry(search_wrapper, textvariable=self.search_var, 
                                   font=('Arial', 11),  # Match dropdown font size
                                   bg=UIConstants.BUTTON_DEFAULT_BG,
                                   fg=UIConstants.BUTTON_DEFAULT_FG,
                                   insertbackground=UIConstants.TEXT_COLOR,
                                   relief='solid', bd=1, width=25,
                                   highlightthickness=0)  # Remove border highlight
        self.search_entry.pack(fill='both', expand=True)
        
        # Profile toolbar on the right - make it scrollable
        toolbar_container = tk.Frame(search_container, bg=UIConstants.BACKGROUND_COLOR)
        toolbar_container.pack(side='right', fill='x', expand=True)
        
        # Create canvas for horizontal scrolling without visible scrollbar
        self.toolbar_canvas = tk.Canvas(toolbar_container, bg=UIConstants.BACKGROUND_COLOR, 
                                       highlightthickness=0, height=50)
        self.toolbar_canvas.pack(fill='x', expand=True)
        
        # Create the actual toolbar frame inside the canvas
        self.toolbar_frame = tk.Frame(self.toolbar_canvas, bg=UIConstants.BACKGROUND_COLOR)
        self.toolbar_canvas_window = self.toolbar_canvas.create_window((0, 0), window=self.toolbar_frame, anchor='nw')
        
        # Configure toolbar scrolling
        def configure_toolbar_scroll(event=None):
            self.toolbar_canvas.configure(scrollregion=self.toolbar_canvas.bbox('all'))
            # Update canvas window height to match canvas
            canvas_height = self.toolbar_canvas.winfo_height()
            if self.toolbar_frame.winfo_reqheight() != canvas_height:
                self.toolbar_canvas.itemconfig(self.toolbar_canvas_window, height=canvas_height)
        
        self.toolbar_frame.bind('<Configure>', configure_toolbar_scroll)
        self.toolbar_canvas.bind('<Configure>', configure_toolbar_scroll)
        
        # Add horizontal mouse wheel scrolling
        def on_toolbar_mousewheel(event):
            try:
                if self.toolbar_canvas.winfo_exists():
                    # Horizontal scroll with mouse wheel
                    self.toolbar_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass
        
        self.toolbar_canvas.bind("<MouseWheel>", on_toolbar_mousewheel)
        toolbar_container.bind("<MouseWheel>", on_toolbar_mousewheel)
        
        # Create [+] button for adding profiles - same size as champion icons
        # Create a blank image of the right size to set button dimensions
        blank_image = tk.PhotoImage(width=UIConstants.CHAMPION_IMAGE_SIZE[0], 
                                   height=UIConstants.CHAMPION_IMAGE_SIZE[1])
        
        self.add_profile_btn = tk.Button(self.toolbar_frame, text="+",
                                       font=('Arial', 12, 'bold'),
                                       bg=UIConstants.BUTTON_DEFAULT_BG,
                                       fg=UIConstants.BUTTON_DEFAULT_FG,
                                       image=blank_image,
                                       compound='center',
                                       relief='solid', bd=2,
                                       highlightthickness=0,
                                       activebackground=UIConstants.BUTTON_DEFAULT_BG,
                                       command=self._on_create_profile)
        # Keep reference to prevent garbage collection
        self.add_profile_btn.image = blank_image
        self.add_profile_btn.pack(side='left', padx=(10, 5))
        
        # Bind mouse wheel scrolling to the [+] button
        def on_add_button_scroll(event):
            try:
                if self.toolbar_canvas.winfo_exists():
                    self.toolbar_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass
        self.add_profile_btn.bind("<MouseWheel>", on_add_button_scroll)
        
        # Horizontal scrollable champion list
        scroll_container = tk.Frame(self.champion_frame, bg=UIConstants.BACKGROUND_COLOR)
        scroll_container.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(scroll_container, bg=UIConstants.BACKGROUND_COLOR, 
                              highlightthickness=0, height=60)
        
        # Style the horizontal scrollbar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Horizontal.TScrollbar", 
                       background=UIConstants.SCROLLBAR_BG, 
                       troughcolor=UIConstants.SCROLLBAR_BG,
                       bordercolor=UIConstants.SCROLLBAR_BORDER, 
                       arrowcolor=UIConstants.SCROLLBAR_ARROW, 
                       darkcolor=UIConstants.SCROLLBAR_BORDER,
                       lightcolor=UIConstants.SCROLLBAR_BG)
        
        self.scrollbar = ttk.Scrollbar(scroll_container, orient="horizontal", command=self.canvas.xview)
        self.champion_list_frame = tk.Frame(self.canvas, bg=UIConstants.BACKGROUND_COLOR)
        
        self.champion_list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.champion_list_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(fill="x", expand=True)
        self.scrollbar.pack(fill="x")
        
        # Bind mousewheel to canvas and scrollbar for horizontal scrolling
        def _on_mousewheel(event):
            self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mousewheel to multiple widgets
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.scrollbar.bind("<MouseWheel>", _on_mousewheel)
        scroll_container.bind("<MouseWheel>", _on_mousewheel)
        
        # Also bind to the champion list frame when it gets created
        def bind_mousewheel_to_champion_frame():
            if hasattr(self, 'champion_list_frame') and self.champion_list_frame.winfo_exists():
                self.champion_list_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Schedule binding after frame creation
        scroll_container.after(100, bind_mousewheel_to_champion_frame)
        
    def set_champion_select_callback(self, callback: Callable):
        """Set callback for champion selection"""
        self.on_champion_select = callback
        
    def set_search_callback(self, callback: Callable):
        """Set callback for search filtering"""
        self.search_var.trace('w', callback)
        
    def display_champions(self, champions_data: List[Tuple]):
        """Display list of champions with efficient loading"""
        self._clear_champion_display()
        
        for champion_id, champion_name, image_path, saved_pages_count in champions_data:
            # Create button with image immediately
            champion_button = self._create_champion_button(champion_id, champion_name, image_path)
            
            self.champion_buttons[champion_id] = champion_button
    
    def _clear_champion_display(self):
        """Clear all champion widgets"""
        for widget in self.champion_list_frame.winfo_children():
            widget.destroy()
        self.champion_buttons.clear()
    
    def _create_champion_button(self, champion_id: int, champion_name: str, image_path: str) -> tk.Button:
        """Create a champion button with image"""
        # Define mousewheel handler for champion buttons
        def _on_mousewheel_champion(event):
            self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        try:
            # Load image synchronously
            champion_image = self.image_loader.load_champion_image(image_path, size=UIConstants.CHAMPION_IMAGE_SIZE)
            button = tk.Button(self.champion_list_frame, image=champion_image,
                              width=UIConstants.CHAMPION_BUTTON_SIZE[0], 
                              height=UIConstants.CHAMPION_BUTTON_SIZE[1], 
                              relief='raised', bd=UIConstants.BORDER_WIDTH,
                              bg=UIConstants.BUTTON_DEFAULT_BG,
                              activebackground=UIConstants.BUTTON_SYSTEM_BG,
                              command=lambda: self._on_champion_clicked(champion_id, champion_name))
            button.image = champion_image  # Keep reference
        except:
            # Fallback to text button if image fails
            button = tk.Button(self.champion_list_frame, text=champion_name[:3],
                              width=UIConstants.CHAMPION_BUTTON_SIZE[0], 
                              height=UIConstants.CHAMPION_BUTTON_SIZE[1], 
                              relief='raised', bd=UIConstants.BORDER_WIDTH,
                              bg=UIConstants.BUTTON_DEFAULT_BG,
                              activebackground=UIConstants.BUTTON_SYSTEM_BG,
                              font=('Arial', 8),
                              command=lambda: self._on_champion_clicked(champion_id, champion_name))
        
        # Bind mousewheel event to the champion button
        button.bind("<MouseWheel>", _on_mousewheel_champion)
        
        # Add tooltip showing champion name and saved matchups
        self._create_champion_tooltip(button, champion_id, champion_name)
        
        button.pack(side='left', padx=UIConstants.CHAMPION_BUTTON_PADDING)
        return button
    
    def _on_champion_clicked(self, champion_id: int, champion_name: str):
        """Handle champion button click - select or deselect"""
        if self.on_champion_select:
            # If clicking on the already selected champion, deselect them
            if self.last_selected_champion == champion_id:
                self.on_champion_select(None, None)  # Deselect
            else:
                self.on_champion_select(champion_id, champion_name)  # Select
            
    def update_selected_champion(self, champion_id: int):
        """Update visual feedback for selected champion"""
        # Reset previously selected champion
        if self.last_selected_champion and self.last_selected_champion in self.champion_buttons:
            self.champion_buttons[self.last_selected_champion].configure(
                relief='raised', bg=UIConstants.BUTTON_DEFAULT_BG)
        
        # Highlight new selection (if not None/deselected)
        if champion_id and champion_id in self.champion_buttons:
            self.champion_buttons[champion_id].configure(
                relief='sunken', bg=UIConstants.CHAMPION_SELECTED_BG)
        
        self.last_selected_champion = champion_id
    
    def update_selected_profile(self, profile_id: Optional[int]):
        """Update visual feedback for selected profile - similar to champion selection"""
        # Reset all profile buttons to default state
        for pid, btn in self.profile_buttons.items():
            btn.configure(relief='solid', bd=2, bg=UIConstants.BUTTON_DEFAULT_BG,
                         activebackground=UIConstants.BUTTON_DEFAULT_BG)
        
        # Highlight the selected profile (if not None)
        if profile_id and profile_id in self.profile_buttons:
            btn = self.profile_buttons[profile_id]
            btn.configure(relief='sunken', bd=2, bg=UIConstants.BUTTON_SELECTED_BG, 
                         activebackground=UIConstants.BUTTON_SELECTED_BG)
        
        self.current_filter_profile_id = profile_id
        
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_var.get()
    
    def set_profile_callbacks(self, on_create: Callable = None, on_edit: Callable = None, 
                             on_filter: Callable = None):
        """Set callbacks for profile operations"""
        self.on_create_profile = on_create
        self.on_edit_profile = on_edit
        self.on_filter_by_profile = on_filter
    
    def _on_create_profile(self):
        """Handle create profile button click"""
        if self.on_create_profile:
            self.on_create_profile()
    
    def add_profile_button(self, profile_id: int, profile_name: str, champion_names: List[str]):
        """Add a profile button to the toolbar"""
        # Get champion data for this profile to select a random champion image
        profile_champion_ids = self.on_filter_by_profile and hasattr(self, '_get_profile_champion_data')
        random_champion_data = self._get_random_champion_from_profile(profile_id)
        
        if random_champion_data:
            champion_id, champion_name, image_path, _ = random_champion_data
            # Load champion image
            try:
                image = self.image_loader.load_champion_image(image_path, UIConstants.CHAMPION_IMAGE_SIZE)
                if not image:
                    raise Exception("No image")
            except:
                # Create placeholder if image fails
                image = tk.PhotoImage(width=UIConstants.CHAMPION_IMAGE_SIZE[0], 
                                    height=UIConstants.CHAMPION_IMAGE_SIZE[1])
            
            profile_btn = tk.Button(self.toolbar_frame,
                                  image=image,
                                  bg=UIConstants.BUTTON_DEFAULT_BG,
                                  relief='solid', bd=2,
                                  highlightthickness=0,  # Remove highlight border
                                  activebackground=UIConstants.BUTTON_DEFAULT_BG,
                                  cursor='hand2',
                                  command=lambda: self._on_profile_filter(profile_id))
            # Keep reference to image
            profile_btn.image = image
        else:
            # Fallback to text if no champion data available - use blank image for sizing
            blank_image = tk.PhotoImage(width=UIConstants.CHAMPION_IMAGE_SIZE[0], 
                                       height=UIConstants.CHAMPION_IMAGE_SIZE[1])
            profile_btn = tk.Button(self.toolbar_frame, text=profile_name[:3].upper(),
                                  font=('Arial', 8, 'bold'),
                                  bg=UIConstants.BUTTON_DEFAULT_BG,
                                  fg=UIConstants.BUTTON_DEFAULT_FG,
                                  image=blank_image,
                                  compound='center',
                                  relief='solid', bd=2,
                                  highlightthickness=0,  # Remove highlight border
                                  activebackground=UIConstants.BUTTON_DEFAULT_BG,
                                  cursor='hand2',
                                  command=lambda: self._on_profile_filter(profile_id))
            # Keep reference to prevent garbage collection
            profile_btn.image = blank_image
        
        profile_btn.pack(side='left', padx=2)
        
        # Bind right click for editing (left click now handled by command parameter)
        profile_btn.bind('<Button-3>', lambda e: self._on_profile_edit(profile_id))
        
        # Bind mouse wheel scrolling to the profile button
        def on_profile_button_scroll(event):
            try:
                if self.toolbar_canvas.winfo_exists():
                    self.toolbar_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass
        profile_btn.bind("<MouseWheel>", on_profile_button_scroll)
        
        # Add tooltip
        self._create_profile_tooltip(profile_btn, profile_name, champion_names)
        
        self.profile_buttons[profile_id] = profile_btn
    
    def _get_random_champion_from_profile(self, profile_id: int):
        """Get a random champion from the profile for the button image"""
        # This will be set by the controller
        if hasattr(self, '_profile_champion_data') and profile_id in self._profile_champion_data:
            champion_ids = self._profile_champion_data[profile_id]
            if champion_ids:
                # Find matching champion data from the main champions list
                for champion_data in getattr(self, '_champions_data', []):
                    if champion_data[0] in champion_ids:
                        return champion_data
        return None
    
    def set_profile_champion_data(self, profile_id: int, champion_ids: List[int]):
        """Set champion data for a profile (called by controller)"""
        if not hasattr(self, '_profile_champion_data'):
            self._profile_champion_data = {}
        self._profile_champion_data[profile_id] = champion_ids
    
    def set_champions_data(self, champions_data):
        """Set the main champions data for reference"""
        self._champions_data = champions_data
    
    def remove_profile_button(self, profile_id: int):
        """Remove a profile button from the toolbar"""
        if profile_id in self.profile_buttons:
            self.profile_buttons[profile_id].destroy()
            del self.profile_buttons[profile_id]
    
    def update_profile_button(self, profile_id: int, profile_name: str, champion_names: List[str]):
        """Update an existing profile button"""
        if profile_id in self.profile_buttons:
            # Remove old button and create new one with updated image
            self.remove_profile_button(profile_id)
            self.add_profile_button(profile_id, profile_name, champion_names)
            
            # Refresh all button states to ensure consistency
            self.refresh_profile_button_states()
    
    def clear_profile_filter(self):
        """Clear the current profile filter"""
        self.current_filter_profile_id = None
        # Reset button appearances (keep consistent border size)
        for btn in self.profile_buttons.values():
            btn.configure(relief='solid', bd=2, bg=UIConstants.BUTTON_DEFAULT_BG,
                         activebackground=UIConstants.BUTTON_DEFAULT_BG)
    
    def refresh_profile_button_states(self):
        """Refresh all profile button visual states to match current filter"""
        for pid, btn in self.profile_buttons.items():
            if pid == self.current_filter_profile_id:
                btn.configure(relief='sunken', bd=2, bg=UIConstants.BUTTON_SELECTED_BG, 
                             activebackground=UIConstants.BUTTON_SELECTED_BG)
            else:
                btn.configure(relief='solid', bd=2, bg=UIConstants.BUTTON_DEFAULT_BG,
                             activebackground=UIConstants.BUTTON_DEFAULT_BG)
    
    def _on_profile_filter(self, profile_id: int):
        """Handle profile filter click"""
        if self.current_filter_profile_id == profile_id:
            # Toggle off if same profile clicked
            self.update_selected_profile(None)  # This sets current_filter_profile_id to None
            if self.on_filter_by_profile:
                self.on_filter_by_profile(None)  # Show all champions
        else:
            # Set new filter - update visual state immediately
            self.update_selected_profile(profile_id)  # This sets current_filter_profile_id
            
            if self.on_filter_by_profile:
                self.on_filter_by_profile(profile_id)
    
    def _on_profile_edit(self, profile_id: int):
        """Handle profile edit right-click"""
        if self.on_edit_profile:
            self.on_edit_profile(profile_id)
    
    def _create_profile_tooltip(self, widget: tk.Widget, profile_name: str, champion_names: List[str]):
        """Create tooltip for profile button"""
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='#2C2C2E', relief='solid', bd=1)
            
            # Create tooltip content
            content = f"{profile_name}\n\n" + "\n".join(f"• {name}" for name in champion_names[:10])
            if len(champion_names) > 10:
                content += f"\n... and {len(champion_names) - 10} more"
            
            label = tk.Label(tooltip, text=content,
                           font=('Arial', 9),
                           bg='#2C2C2E', fg='white',
                           justify='left', padx=8, pady=6)
            label.pack()
            
            # Position tooltip
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.geometry(f"+{x}+{y}")
            
            # Auto-hide after delay
            widget.tooltip = tooltip
            widget.after(3000, lambda: tooltip.destroy() if tooltip.winfo_exists() else None)
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip') and widget.tooltip.winfo_exists():
                widget.tooltip.destroy()
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def _create_champion_tooltip(self, widget: tk.Widget, champion_id: int, champion_name: str):
        """Create tooltip for champion button showing name and saved matchups"""
        def show_tooltip(event):
            # Get saved matchups for this champion
            matchups = self._get_champion_matchups(champion_id)
            
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='#2C2C2E', relief='solid', bd=1)
            
            # Create tooltip content
            if matchups:
                content = f"{champion_name}\n\n" + "\n".join(matchups)
            else:
                content = champion_name
            
            label = tk.Label(tooltip, text=content,
                           font=('Arial', 9),
                           bg='#2C2C2E', fg='white',
                           justify='left', padx=8, pady=6)
            label.pack()
            
            # Position tooltip
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.geometry(f"+{x}+{y}")
            
            # Auto-hide after delay
            widget.tooltip = tooltip
            widget.after(3000, lambda: tooltip.destroy() if tooltip.winfo_exists() else None)
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip') and widget.tooltip.winfo_exists():
                widget.tooltip.destroy()
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def _get_champion_matchups(self, champion_id: int) -> List[str]:
        """Get saved matchup names for a champion"""
        if self.on_get_champion_matchups:
            return self.on_get_champion_matchups(champion_id)
        return []
    
    def set_champion_matchups_callback(self, callback: Callable):
        """Set callback to get champion matchups for tooltips"""
        self.on_get_champion_matchups = callback