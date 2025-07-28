import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List
from views.ui_constants import UIConstants


class SavePanelView:
    """View component for save panel with action buttons"""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.on_save: Optional[Callable] = None
        self.on_clear: Optional[Callable] = None
        self.on_save_new: Optional[Callable] = None
        self.champion_names: List[str] = []  # Will be populated by controller
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup save panel UI"""
        # Clean save container
        save_container = tk.Frame(self.parent, bg=UIConstants.BACKGROUND_COLOR, relief='solid', bd=1)
        save_container.pack(fill='x', pady=(10, 8))
        
        # Input fields with clean layout
        inputs_frame = tk.Frame(save_container, bg=UIConstants.BACKGROUND_COLOR)
        inputs_frame.pack(fill='x', padx=12, pady=8)
        
        # Matchup with buttons on same row
        name_frame = tk.Frame(inputs_frame, bg=UIConstants.BACKGROUND_COLOR)
        name_frame.pack(fill='x', pady=(0, 6))
        tk.Label(name_frame, text="Matchup:", font=('Arial', 11), 
                fg=UIConstants.TEXT_COLOR, bg=UIConstants.BACKGROUND_COLOR, width=15, anchor='w').pack(side='left')
        
        # Create autocomplete entry with custom dropdown
        self.matchup_var = tk.StringVar()
        self.matchup_entry = tk.Entry(name_frame, textvariable=self.matchup_var, 
                                    font=('Arial', 11), width=32, relief='solid', bd=1,
                                    bg=UIConstants.BUTTON_DEFAULT_BG, fg=UIConstants.BUTTON_DEFAULT_FG, 
                                    insertbackground=UIConstants.TEXT_COLOR)
        self.matchup_entry.pack(side='left', padx=(10, 10))
        
        # Create suggestion listbox (initially hidden)
        self.suggestion_frame = None
        self.suggestion_listbox = None
        
        # Bind events for autocomplete functionality
        self.matchup_entry.bind('<KeyRelease>', self._on_keyrelease)
        self.matchup_entry.bind('<Button-1>', self._on_click)
        self.matchup_entry.bind('<FocusOut>', self._on_focus_out)
        self.matchup_entry.bind('<Tab>', self._on_tab_key)
        
        # Buttons on same row as name entry
        self.clear_btn = tk.Button(name_frame, text="Clear", font=('Arial', 10),
                                  command=self._on_clear_clicked, bg=UIConstants.DELETE_BUTTON_FG, fg=UIConstants.BACKGROUND_COLOR,
                                  relief='flat', padx=12, pady=4, cursor='hand2')
        self.clear_btn.pack(side='left', padx=(0, 5))
        
        self.save_btn = tk.Button(name_frame, text="Save", font=('Arial', 10),
                                 command=self._on_save_clicked, bg=UIConstants.BUTTON_SELECTED_BG, fg=UIConstants.BUTTON_SELECTED_FG,
                                 relief='flat', padx=12, pady=4, cursor='hand2')
        self.save_btn.pack(side='left', padx=(0, 5))
        
        self.save_new_btn = tk.Button(name_frame, text="Save As", font=('Arial', 10),
                                     command=self._on_save_new_clicked, bg=UIConstants.BUTTON_DEFAULT_BG, fg=UIConstants.BUTTON_DEFAULT_FG,
                                     relief='flat', padx=8, pady=4, cursor='hand2')
        self.save_new_btn.pack(side='left')
        
        # Matchup notes on separate row
        notes_frame = tk.Frame(inputs_frame, bg=UIConstants.BACKGROUND_COLOR)
        notes_frame.pack(fill='x')
        tk.Label(notes_frame, text="Matchup Notes:", font=('Arial', 11), 
                fg=UIConstants.TEXT_COLOR, bg=UIConstants.BACKGROUND_COLOR, width=15, anchor='w').pack(side='left', anchor='n')
        self.notes_text = tk.Text(notes_frame, height=2, width=32, font=('Arial', 11),
                                 relief='solid', bd=1, bg=UIConstants.BUTTON_DEFAULT_BG, 
                                 fg=UIConstants.BUTTON_DEFAULT_FG, insertbackground=UIConstants.TEXT_COLOR)
        self.notes_text.pack(side='left', padx=(10, 0))
        
    def set_callbacks(self, on_save: Callable, on_clear: Callable, on_save_new: Callable = None):
        """Set callbacks for save, clear, and save new actions"""
        self.on_save = on_save
        self.on_clear = on_clear
        self.on_save_new = on_save_new
        
    def _on_save_clicked(self):
        """Handle save button click"""
        if self.on_save:
            self.on_save()
            
    def _on_clear_clicked(self):
        """Handle clear button click"""
        if self.on_clear:
            self.on_clear()
            
    def _on_save_new_clicked(self):
        """Handle save new button click"""
        if self.on_save_new:
            self.on_save_new()
            
    def get_rune_page_name(self) -> str:
        """Get the entered matchup name"""
        return self.matchup_var.get().strip()
        
    def get_notes(self) -> str:
        """Get the entered notes"""
        return self.notes_text.get("1.0", tk.END).strip()
        
    def clear_inputs(self):
        """Clear input fields"""
        self.matchup_var.set('')
        self.notes_text.delete("1.0", tk.END)
        
    def enable_save_new_button(self):
        """Enable the Save As button - no longer needed"""
        pass
        
    def disable_save_new_button(self):
        """Disable the Save As button - no longer needed"""
        pass
        
    def set_champion_names(self, champion_names: List[str]):
        """Set the list of valid champion names for autocomplete"""
        # Clean champion names by stripping whitespace
        self.champion_names = sorted([name.strip() for name in champion_names if name.strip()])
        
    def _on_keyrelease(self, event):
        """Handle key release for autocomplete functionality"""
        # Handle navigation in suggestion list
        if self.suggestion_listbox and self.suggestion_listbox.winfo_exists():
            if event.keysym == 'Down':
                try:
                    current = self.suggestion_listbox.curselection()
                    if current:
                        next_index = min(current[0] + 1, self.suggestion_listbox.size() - 1)
                    else:
                        next_index = 0
                    self.suggestion_listbox.selection_clear(0, tk.END)
                    self.suggestion_listbox.selection_set(next_index)
                    self.suggestion_listbox.see(next_index)
                except:
                    pass
                return
            elif event.keysym == 'Up':
                try:
                    current = self.suggestion_listbox.curselection()
                    if current:
                        next_index = max(current[0] - 1, 0)
                    else:
                        next_index = 0
                    self.suggestion_listbox.selection_clear(0, tk.END)
                    self.suggestion_listbox.selection_set(next_index)
                    self.suggestion_listbox.see(next_index)
                except:
                    pass
                return
            elif event.keysym == 'Return':
                self._select_suggestion()
                return
            elif event.keysym == 'Escape':
                self._hide_suggestions()
                return
        
        # Filter and show suggestions
        current_text = self.matchup_var.get().strip()
        
        if not current_text:
            self._hide_suggestions()
            self.matchup_entry.configure(fg=UIConstants.BUTTON_DEFAULT_FG)
            return
            
        # Filter champion names based on current input
        matching_champions = [name for name in self.champion_names 
                            if current_text.lower() in name.lower()]
        
        if matching_champions:
            self._show_suggestions(matching_champions)
            # Check for exact match
            exact_match = any(name.lower() == current_text.lower() for name in self.champion_names)
            self.matchup_entry.configure(fg=UIConstants.BUTTON_DEFAULT_FG if exact_match else UIConstants.TEXT_COLOR)
        else:
            self._hide_suggestions()
            self.matchup_entry.configure(fg='#FF6B6B')  # Red for invalid
            
    def _on_click(self, event):
        """Handle click on entry field"""
        current_text = self.matchup_var.get().strip()
        if current_text:
            matching_champions = [name for name in self.champion_names 
                                if current_text.lower() in name.lower()]
            if matching_champions:
                self._show_suggestions(matching_champions)
    
    def _on_focus_out(self, event):
        """Handle focus out - delay hiding to allow selection"""
        # Delay hiding suggestions to allow clicking on listbox
        self.matchup_entry.after(150, self._hide_suggestions)
    
    def _on_tab_key(self, event):
        """Handle Tab key to move focus to notes field"""
        # Hide suggestions when tabbing away
        self._hide_suggestions()
        # Move focus to notes text area
        self.notes_text.focus_set()
        # Prevent default Tab behavior
        return 'break'
        
    def _validate_champion_for_save(self):
        """Validate champion name only when saving (not during typing)"""
        entered_text = self.matchup_var.get().strip()
        
        if not entered_text:
            return True  # Empty is allowed (will be treated as "Generic")
            
        # Allow "Generic" as a special case
        if entered_text.lower() == "generic":
            return True
            
        # Check if entered text matches any champion name (case-insensitive)
        for champion in self.champion_names:
            if champion.lower() == entered_text.lower():
                # Auto-correct to proper capitalization
                self.matchup_var.set(champion)
                return True
                
        return False
            
    def is_valid_matchup(self) -> bool:
        """Check if current matchup input is valid"""
        return self._validate_champion_for_save()
    
    def _show_suggestions(self, suggestions: List[str]):
        """Show autocomplete suggestions in a listbox"""
        if not suggestions:
            self._hide_suggestions()
            return
            
        # Calculate dynamic height based on number of suggestions
        num_suggestions = len(suggestions)
        max_visible = min(6, num_suggestions)  # Show max 6 items
        listbox_height = max_visible * 20  # ~20px per item
        
        # Create suggestion frame if it doesn't exist or recreate for positioning
        if self.suggestion_frame:
            try:
                self.suggestion_frame.destroy()
            except:
                pass
            
        # Get the absolute position of the entry widget
        self.matchup_entry.update_idletasks()  # Ensure geometry is updated
        entry_x = self.matchup_entry.winfo_rootx()
        entry_y = self.matchup_entry.winfo_rooty() + self.matchup_entry.winfo_height()
        entry_width = self.matchup_entry.winfo_width()
        
        # Create toplevel window for suggestions
        self.suggestion_frame = tk.Toplevel(self.matchup_entry.winfo_toplevel())
        self.suggestion_frame.wm_overrideredirect(True)
        self.suggestion_frame.configure(bg=UIConstants.BACKGROUND_COLOR, relief='solid', bd=1)
        
        # Position directly below the entry widget (closer positioning)
        self.suggestion_frame.geometry(f"{entry_width}x{listbox_height + 4}+{entry_x}+{entry_y}")
        
        # Create listbox for suggestions
        self.suggestion_listbox = tk.Listbox(
            self.suggestion_frame,
            height=max_visible,
            font=('Arial', 11),
            bg=UIConstants.BUTTON_DEFAULT_BG,
            fg=UIConstants.BUTTON_DEFAULT_FG,
            selectbackground=UIConstants.BUTTON_SELECTED_BG,
            selectforeground=UIConstants.BUTTON_SELECTED_FG,
            relief='flat',
            bd=0,
            activestyle='none'
        )
        self.suggestion_listbox.pack(fill='both', expand=True, padx=1, pady=1)
        self.suggestion_listbox.bind('<Double-Button-1>', lambda e: self._select_suggestion())
        self.suggestion_listbox.bind('<Button-1>', lambda e: self.matchup_entry.after(200, self._select_suggestion))
        
        # Clear and populate listbox
        self.suggestion_listbox.delete(0, tk.END)
        for suggestion in suggestions:
            self.suggestion_listbox.insert(tk.END, suggestion)
        
        # Show the suggestion frame
        self.suggestion_frame.deiconify()
    
    def _hide_suggestions(self):
        """Hide the autocomplete suggestions"""
        if self.suggestion_frame and self.suggestion_frame.winfo_exists():
            try:
                self.suggestion_frame.withdraw()
            except:
                pass
    
    def _select_suggestion(self):
        """Select the currently highlighted suggestion"""
        if self.suggestion_listbox and self.suggestion_listbox.winfo_exists():
            try:
                selection = self.suggestion_listbox.curselection()
                if selection:
                    selected_text = self.suggestion_listbox.get(selection[0])
                    self.matchup_var.set(selected_text)
                    self.matchup_entry.configure(fg=UIConstants.BUTTON_DEFAULT_FG)
                    self._hide_suggestions()
                    self.matchup_entry.focus_set()
            except:
                pass