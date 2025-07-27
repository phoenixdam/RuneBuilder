import tkinter as tk
from typing import Callable, Optional
from views.ui_constants import UIConstants


class SavePanelView:
    """View component for save panel with action buttons"""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.on_save: Optional[Callable] = None
        self.on_clear: Optional[Callable] = None
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup save panel UI"""
        # Clean save container
        save_container = tk.Frame(self.parent, bg=UIConstants.BACKGROUND_COLOR, relief='solid', bd=1)
        save_container.pack(fill='x', pady=(10, 8))
        
        # Input fields with clean layout
        inputs_frame = tk.Frame(save_container, bg=UIConstants.BACKGROUND_COLOR)
        inputs_frame.pack(fill='x', padx=12, pady=8)
        
        # Rune page name with buttons on same row
        name_frame = tk.Frame(inputs_frame, bg=UIConstants.BACKGROUND_COLOR)
        name_frame.pack(fill='x', pady=(0, 6))
        tk.Label(name_frame, text="Rune Page Name:", font=('Arial', 11), 
                fg=UIConstants.TEXT_COLOR, bg=UIConstants.BACKGROUND_COLOR, width=15, anchor='w').pack(side='left')
        self.name_entry = tk.Entry(name_frame, font=('Arial', 11), width=32,
                                  relief='solid', bd=1, bg=UIConstants.BUTTON_DEFAULT_BG, 
                                  fg=UIConstants.BUTTON_DEFAULT_FG, insertbackground=UIConstants.TEXT_COLOR)
        self.name_entry.pack(side='left', padx=(10, 10))
        
        # Buttons on same row as name entry
        self.clear_btn = tk.Button(name_frame, text="Clear", font=('Arial', 10),
                                  command=self._on_clear_clicked, bg=UIConstants.DELETE_BUTTON_FG, fg=UIConstants.BACKGROUND_COLOR,
                                  relief='flat', padx=12, pady=4, cursor='hand2')
        self.clear_btn.pack(side='left', padx=(0, 5))
        
        self.save_btn = tk.Button(name_frame, text="Save", font=('Arial', 10),
                                 command=self._on_save_clicked, bg=UIConstants.BUTTON_SELECTED_BG, fg=UIConstants.BUTTON_SELECTED_FG,
                                 relief='flat', padx=12, pady=4, cursor='hand2')
        self.save_btn.pack(side='left')
        
        # Matchup notes on separate row
        notes_frame = tk.Frame(inputs_frame, bg=UIConstants.BACKGROUND_COLOR)
        notes_frame.pack(fill='x')
        tk.Label(notes_frame, text="Matchup Notes:", font=('Arial', 11), 
                fg=UIConstants.TEXT_COLOR, bg=UIConstants.BACKGROUND_COLOR, width=15, anchor='w').pack(side='left', anchor='n')
        self.notes_text = tk.Text(notes_frame, height=2, width=32, font=('Arial', 11),
                                 relief='solid', bd=1, bg=UIConstants.BUTTON_DEFAULT_BG, 
                                 fg=UIConstants.BUTTON_DEFAULT_FG, insertbackground=UIConstants.TEXT_COLOR)
        self.notes_text.pack(side='left', padx=(10, 0))
        
    def set_callbacks(self, on_save: Callable, on_clear: Callable):
        """Set callbacks for save and clear actions"""
        self.on_save = on_save
        self.on_clear = on_clear
        
    def _on_save_clicked(self):
        """Handle save button click"""
        if self.on_save:
            self.on_save()
            
    def _on_clear_clicked(self):
        """Handle clear button click"""
        if self.on_clear:
            self.on_clear()
            
    def get_rune_page_name(self) -> str:
        """Get the entered rune page name"""
        return self.name_entry.get().strip()
        
    def get_notes(self) -> str:
        """Get the entered notes"""
        return self.notes_text.get("1.0", tk.END).strip()
        
    def clear_inputs(self):
        """Clear input fields"""
        self.name_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)