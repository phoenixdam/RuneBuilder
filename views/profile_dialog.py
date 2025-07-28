import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Callable, Optional, Set
from views.ui_constants import UIConstants
from views.image_loader import ImageLoader


class ProfileDialog:
    """Dialog for creating/editing champion profiles"""
    
    def __init__(self, parent: tk.Widget, image_loader: ImageLoader, 
                 champions_data: List[Tuple], profile_data: Optional[Tuple] = None,
                 selected_champion_ids: Optional[Set[int]] = None):
        self.parent = parent
        self.image_loader = image_loader
        self.champions_data = champions_data
        self.selected_champion_ids = selected_champion_ids or set()
        self.profile_data = profile_data  # (profile_id, name) if editing
        self.result = None  # Will store (name, champion_ids) if saved
        
        self._create_dialog()
        
    def _create_dialog(self):
        """Create the profile dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Edit Profile" if self.profile_data else "Create Profile")
        self.dialog.geometry("600x500")
        self.dialog.configure(bg=UIConstants.BACKGROUND_COLOR)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create header frame
        header_frame = tk.Frame(self.dialog, bg=UIConstants.BACKGROUND_COLOR)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # Name input on the left
        tk.Label(header_frame, text="Profile Name:", 
                bg=UIConstants.BACKGROUND_COLOR, 
                fg=UIConstants.TEXT_COLOR,
                font=('Arial', UIConstants.FONT_SIZE_DEFAULT)).pack(side='left')
        
        self.name_var = tk.StringVar()
        if self.profile_data:
            self.name_var.set(self.profile_data[1])  # Set existing name without truncation
            
        self.name_entry = tk.Entry(header_frame, textvariable=self.name_var,
                                  font=('Arial', UIConstants.FONT_SIZE_DEFAULT),
                                  bg=UIConstants.BUTTON_DEFAULT_BG,
                                  fg=UIConstants.BUTTON_DEFAULT_FG,
                                  width=20)
        self.name_entry.pack(side='left', padx=(10, 0))
        
        # Save button on the right
        tk.Button(header_frame, text="Save",
                 font=('Arial', UIConstants.FONT_SIZE_DEFAULT),
                 bg=UIConstants.BUTTON_SELECTED_BG,
                 fg=UIConstants.BUTTON_SELECTED_FG,
                 command=self._save_profile).pack(side='right')
        
        # Delete button (only show when editing)
        if self.profile_data:  # Only show delete button when editing existing profile
            tk.Button(header_frame, text="Delete",
                     font=('Arial', UIConstants.FONT_SIZE_DEFAULT),
                     bg=UIConstants.BUTTON_DEFAULT_BG,
                     fg=UIConstants.DELETE_BUTTON_FG,
                     command=self._delete_profile).pack(side='right', padx=(0, 5))
        
        # Cancel button
        tk.Button(header_frame, text="Cancel",
                 font=('Arial', UIConstants.FONT_SIZE_DEFAULT),
                 bg=UIConstants.BUTTON_DEFAULT_BG,
                 fg=UIConstants.BUTTON_DEFAULT_FG,
                 command=self._cancel).pack(side='right', padx=(0, 5))
        
        # Create scrollable champion grid
        self._create_champion_grid()
        
        # Focus on name entry
        self.name_entry.focus_set()
        
        # Bind escape to cancel
        self.dialog.bind('<Escape>', lambda e: self._cancel())
        
    def _create_champion_grid(self):
        """Create scrollable grid of champion selection buttons"""
        # Create frame with scrollbar
        main_frame = tk.Frame(self.dialog, bg=UIConstants.BACKGROUND_COLOR)
        main_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))
        
        # Create canvas and vertical scrollbar only
        canvas = tk.Canvas(main_frame, bg=UIConstants.BACKGROUND_COLOR, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Pack scrollbar and canvas
        v_scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        
        # Create scrollable frame
        scrollable_frame = tk.Frame(canvas, bg=UIConstants.BACKGROUND_COLOR)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        
        # Configure scrolling
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Make the scrollable_frame fill the canvas width to eliminate blank space
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind('<Configure>', configure_scroll_region)
        canvas.bind('<Configure>', configure_scroll_region)
        
        # Bind mousewheel to canvas with error handling
        def on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass  # Ignore errors if canvas is destroyed
        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        
        # Create champion buttons in grid
        self.champion_buttons = {}
        
        # Calculate optimal champions per row based on available width
        # Dialog is 600px, minus padding (20px) and scrollbar (~20px), leaves ~560px
        # Champion button width is typically ~50px + padding, so about 10-11 champions fit
        champions_per_row = 10
        
        for i, (champion_id, name, image_path, rune_count) in enumerate(self.champions_data):
            row = i // champions_per_row
            col = i % champions_per_row
            
            # Create button frame
            btn_frame = tk.Frame(scrollable_frame, bg=UIConstants.BACKGROUND_COLOR)
            btn_frame.grid(row=row, column=col, padx=2, pady=2)
            
            # Bind mousewheel scrolling to button frame
            btn_frame.bind("<MouseWheel>", on_mousewheel)
            
            # Load champion image
            try:
                image = self.image_loader.load_champion_image(image_path, UIConstants.CHAMPION_IMAGE_SIZE)
                if not image:
                    raise Exception("No image")
            except:
                # Create placeholder if image fails
                image = tk.PhotoImage(width=UIConstants.CHAMPION_IMAGE_SIZE[0], 
                                    height=UIConstants.CHAMPION_IMAGE_SIZE[1])
            
            # Create toggle button with consistent border width and only color changes
            is_selected = champion_id in self.selected_champion_ids
            btn = tk.Button(btn_frame, 
                           image=image,
                           width=UIConstants.CHAMPION_BUTTON_SIZE[0],
                           height=UIConstants.CHAMPION_BUTTON_SIZE[1],
                           bg=UIConstants.BUTTON_SELECTED_BG if is_selected else UIConstants.BUTTON_DEFAULT_BG,
                           activebackground=UIConstants.BUTTON_SELECTED_BG,
                           relief='solid',
                           bd=2,  # Always use 2px border
                           highlightcolor=UIConstants.BUTTON_SELECTED_FG if is_selected else UIConstants.BUTTON_DEFAULT_BG,
                           command=lambda cid=champion_id: self._toggle_champion(cid))
            btn.pack()
            
            # Keep reference to image
            btn.image = image
            
            # Bind mousewheel scrolling to button
            btn.bind("<MouseWheel>", on_mousewheel)
            
            # Store button reference
            self.champion_buttons[champion_id] = btn
            
            # Add champion name label (limited to 5 characters)
            display_name = name[:5] if len(name) > 5 else name
            name_label = tk.Label(btn_frame, text=display_name,
                                font=('Arial', 8),
                                bg=UIConstants.BACKGROUND_COLOR,
                                fg=UIConstants.TEXT_COLOR,
                                wraplength=UIConstants.CHAMPION_BUTTON_SIZE[0])
            name_label.pack()
            
            # Bind mousewheel scrolling to name label as well
            name_label.bind("<MouseWheel>", on_mousewheel)
        
        # Update scroll region after all widgets are added
        scrollable_frame.update_idletasks()
        configure_scroll_region()
        
    def _toggle_champion(self, champion_id: int):
        """Toggle champion selection"""
        if champion_id in self.selected_champion_ids:
            self.selected_champion_ids.remove(champion_id)
            # Update button appearance - deselected (only background color changes)
            self.champion_buttons[champion_id].configure(
                bg=UIConstants.BUTTON_DEFAULT_BG,
                highlightcolor=UIConstants.BUTTON_DEFAULT_BG
            )
        else:
            self.selected_champion_ids.add(champion_id)
            # Update button appearance - selected (only background color changes)
            self.champion_buttons[champion_id].configure(
                bg=UIConstants.BUTTON_SELECTED_BG,
                highlightcolor=UIConstants.BUTTON_SELECTED_FG
            )
    
    def _save_profile(self):
        """Save the profile"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a profile name!")
            return
            
        if not self.selected_champion_ids:
            messagebox.showwarning("No Champions", "Please select at least one champion!")
            return
        
        self.result = ('save', name, list(self.selected_champion_ids))
        self.dialog.destroy()
    
    def _delete_profile(self):
        """Delete the profile"""
        if not self.profile_data:
            return
            
        # Confirm deletion
        from tkinter import messagebox
        result = messagebox.askyesno("Delete Profile", 
                                   f"Are you sure you want to delete the profile '{self.profile_data[1]}'?\n\nThis action cannot be undone.")
        if result:
            self.result = ('delete', self.profile_data[0])  # Return action and profile_id
            self.dialog.destroy()
        
    def _cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.dialog.destroy()
        
    def show(self) -> Optional[Tuple]:
        """Show the dialog and return result
        
        Returns:
            None if cancelled
            ('save', name, champion_ids) if saved
            ('delete', profile_id) if deleted
        """
        self.dialog.wait_window()
        return self.result