import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Callable, Dict, Optional
from views.ui_constants import UIConstants
from views.image_loader import ImageLoader


class ChampionView:
    """View component for champion selection panel"""
    
    def __init__(self, parent: tk.Widget, image_loader: ImageLoader):
        self.parent = parent
        self.image_loader = image_loader
        self.champion_buttons: Dict[int, tk.Button] = {}
        self.last_selected_champion: Optional[int] = None
        self.on_champion_select: Optional[Callable] = None
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup champion selection panel UI with grid layout"""
        self.champion_frame = tk.Frame(self.parent, bg=UIConstants.BACKGROUND_COLOR, 
                                     width=UIConstants.CHAMPION_FRAME_WIDTH)
        self.champion_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 0))
        self.champion_frame.grid_propagate(False)
        
        # Search box
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.champion_frame, textvariable=self.search_var, 
                                   font=('Arial', UIConstants.FONT_SIZE_DEFAULT),
                                   bg=UIConstants.BUTTON_DEFAULT_BG,
                                   fg=UIConstants.BUTTON_DEFAULT_FG,
                                   insertbackground=UIConstants.TEXT_COLOR,
                                   relief='solid', bd=1)
        self.search_entry.pack(fill='x')
        
        # Scrollable champion list
        self.canvas = tk.Canvas(self.champion_frame, bg=UIConstants.BACKGROUND_COLOR, 
                              highlightthickness=0, width=UIConstants.CHAMPION_CANVAS_WIDTH)
        
        # Style the scrollbar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar", 
                       background=UIConstants.SCROLLBAR_BG, 
                       troughcolor=UIConstants.SCROLLBAR_BG,
                       bordercolor=UIConstants.SCROLLBAR_BORDER, 
                       arrowcolor=UIConstants.SCROLLBAR_ARROW, 
                       darkcolor=UIConstants.SCROLLBAR_BORDER,
                       lightcolor=UIConstants.SCROLLBAR_BG)
        
        self.scrollbar = ttk.Scrollbar(self.champion_frame, orient="vertical", command=self.canvas.yview)
        self.champion_list_frame = tk.Frame(self.canvas, bg=UIConstants.BACKGROUND_COLOR)
        
        self.champion_list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.champion_list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        
    def set_champion_select_callback(self, callback: Callable):
        """Set callback for champion selection"""
        self.on_champion_select = callback
        
    def set_search_callback(self, callback: Callable):
        """Set callback for search filtering"""
        self.search_var.trace('w', callback)
        
    def display_champions(self, champions_data: List[Tuple]):
        """Display list of champions with rune counts"""
        self._clear_champion_display()
        
        for champion_id, champion_name, image_path, saved_pages_count in champions_data:
            champion_button = self._create_champion_button(champion_id, champion_name, image_path)
            
            if saved_pages_count > 0:
                self._add_rune_count_label(saved_pages_count)
            
            self.champion_buttons[champion_id] = champion_button
    
    def _clear_champion_display(self):
        """Clear all champion widgets"""
        for widget in self.champion_list_frame.winfo_children():
            widget.destroy()
        self.champion_buttons.clear()
    
    def _create_champion_button(self, champion_id: int, champion_name: str, image_path: str) -> tk.Button:
        """Create a champion button with image"""
        champion_image = self.image_loader.load_champion_image(image_path, size=UIConstants.CHAMPION_IMAGE_SIZE)
        
        button = tk.Button(self.champion_list_frame, image=champion_image,
                          width=UIConstants.CHAMPION_BUTTON_SIZE[0], 
                          height=UIConstants.CHAMPION_BUTTON_SIZE[1], 
                          relief='raised', bd=UIConstants.BORDER_WIDTH,
                          bg=UIConstants.BUTTON_DEFAULT_BG,
                          activebackground=UIConstants.BUTTON_SYSTEM_BG,
                          command=lambda: self._on_champion_clicked(champion_id, champion_name))
        button.image = champion_image  # Keep reference
        button.pack(pady=UIConstants.CHAMPION_BUTTON_PADDING)
        return button
    
    def _add_rune_count_label(self, rune_count: int):
        """Add rune count label below champion button"""
        count_label = tk.Label(self.champion_list_frame, text=f"({rune_count})",
                              font=('Arial', UIConstants.FONT_SIZE_DEFAULT), 
                              fg=UIConstants.TEXT_COLOR,
                              bg=UIConstants.BACKGROUND_COLOR)
        count_label.pack()
        
    def _on_champion_clicked(self, champion_id: int, champion_name: str):
        """Handle champion button click"""
        if self.on_champion_select:
            self.on_champion_select(champion_id, champion_name)
            
    def update_selected_champion(self, champion_id: int):
        """Update visual feedback for selected champion"""
        # Reset previously selected champion
        if self.last_selected_champion and self.last_selected_champion in self.champion_buttons:
            self.champion_buttons[self.last_selected_champion].configure(
                relief='raised', bg=UIConstants.BUTTON_DEFAULT_BG)
        
        # Highlight new selection
        if champion_id in self.champion_buttons:
            self.champion_buttons[champion_id].configure(
                relief='sunken', bg=UIConstants.CHAMPION_SELECTED_BG)
        
        self.last_selected_champion = champion_id
        
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_var.get()