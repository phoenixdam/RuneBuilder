import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Callable, Optional
from views.ui_constants import UIConstants
from views.image_loader import ImageLoader


class SavedRunesView:
    """View component for saved rune pages panel"""
    
    def __init__(self, parent: tk.Widget, image_loader: ImageLoader):
        self.parent = parent
        self.image_loader = image_loader
        self.on_load_rune_page: Optional[Callable] = None
        self.on_set_default: Optional[Callable] = None
        self.on_delete_rune_page: Optional[Callable] = None
        self.on_get_rune_details: Optional[Callable] = None  # Callback to get detailed rune data
        self.rune_pages_data = []
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup saved runes panel UI as dropdown"""
        saved_container = tk.Frame(self.parent, bg=UIConstants.BACKGROUND_COLOR)
        saved_container.pack(fill='x', pady=UIConstants.SAVED_RUNES_PADDING)
        
        # Dropdown container
        dropdown_frame = tk.Frame(saved_container, bg=UIConstants.BACKGROUND_COLOR)
        dropdown_frame.pack(side='left')
        
        # Custom dropdown with tooltip support
        self.selected_page = tk.StringVar()
        self.dropdown_frame = tk.Frame(dropdown_frame, bg=UIConstants.BACKGROUND_COLOR)
        self.dropdown_frame.pack()
        
        # Main dropdown button
        self.dropdown_button = tk.Button(
            self.dropdown_frame,
            textvariable=self.selected_page,
            font=('Arial', 11),
            bg=UIConstants.BUTTON_DEFAULT_BG,
            fg=UIConstants.BUTTON_DEFAULT_FG,
            activebackground=UIConstants.BUTTON_DEFAULT_BG,
            activeforeground=UIConstants.BUTTON_DEFAULT_FG,
            relief='solid',
            bd=1,
            width=25,
            height=1,  # Set consistent height
            anchor='w',
            command=self._toggle_dropdown
        )
        self.dropdown_button.pack()
        
        # Dropdown arrow indicator
        arrow_text = " ▼"
        self.dropdown_button.configure(text=self.selected_page.get() + arrow_text)
        self.selected_page.trace('w', self._update_button_text)
        
        # Custom listbox for dropdown items
        self.dropdown_list = None
        self.dropdown_open = False
        
        # Tooltip functionality
        self.tooltip = None
        self.hover_after_id = None
        
        # Buttons frame
        buttons_frame = tk.Frame(saved_container, bg=UIConstants.BACKGROUND_COLOR)
        buttons_frame.pack(side='left', padx=(10, 0))
        
        # Set Default button - smaller width, text just "Default"
        self.default_btn = tk.Button(buttons_frame, text="Default",
                                   font=('Arial', UIConstants.FONT_SIZE_DEFAULT),
                                   bg=UIConstants.BUTTON_DEFAULT_BG,
                                   fg=UIConstants.BUTTON_DEFAULT_FG,
                                   width=8,  # Smaller width
                                   command=self._on_set_default)
        self.default_btn.pack(side='left', padx=(0, 5))
        
        # Delete button - match Default button width
        self.delete_btn = tk.Button(buttons_frame, text="Delete",
                                  font=('Arial', UIConstants.FONT_SIZE_DEFAULT),
                                  bg=UIConstants.BUTTON_DEFAULT_BG,
                                  fg=UIConstants.DELETE_BUTTON_FG,
                                  width=8,  # Match Default button width
                                  command=self._on_delete)
        self.delete_btn.pack(side='left')
        
    def set_callbacks(self, on_load: Callable, on_set_default: Callable, on_delete: Callable, on_get_rune_details: Callable = None):
        """Set callbacks for rune page operations"""
        self.on_load_rune_page = on_load
        self.on_set_default = on_set_default
        self.on_delete_rune_page = on_delete
        self.on_get_rune_details = on_get_rune_details
        
    def display_rune_pages(self, rune_pages: List[Tuple]):
        """Display saved rune pages in dropdown"""
        # Store rune pages data
        self.rune_pages_data = rune_pages
        
        # Clear dropdown
        self.selected_page.set('')
        
        if not rune_pages:
            self.selected_page.set('No saved rune pages')
            self.dropdown_values = []  # Clear dropdown values when no rune pages
            self.default_btn.configure(state='disabled')
            self.delete_btn.configure(state='disabled')
            return
            
        # Populate dropdown with rune page names
        dropdown_values = []
        default_page = None
        
        for page_id, name, primary_tree, secondary_tree, keystone, notes, is_default in rune_pages:
            display_name = f"vs. {name}"  # Add "vs." prefix to saved rune pages
            if bool(is_default):
                display_name += " (Default)"
                default_page = display_name
            dropdown_values.append(display_name)
        
        self.dropdown_values = dropdown_values
        
        # Don't auto-select any page - user should manually choose
        # Show count of available saved runes
        if dropdown_values:
            self.selected_page.set(f"{len(dropdown_values)} saved rune pages")
        
        # Disable buttons until user selects a specific rune page
        self.default_btn.configure(state='disabled')
        self.delete_btn.configure(state='disabled')
    
    def clear_selection(self):
        """Clear the current dropdown selection"""
        self.selected_page.set('')
        self.default_btn.configure(state='disabled')
        self.delete_btn.configure(state='disabled')
        
    def clear_all(self):
        """Clear all dropdown content and reset to empty state"""
        # Close dropdown if open
        if self.dropdown_open:
            self._close_dropdown()
        
        # Hide any active tooltips first
        self._hide_tooltip()
        if hasattr(self, 'hover_after_id') and self.hover_after_id:
            self.dropdown_button.after_cancel(self.hover_after_id)
            self.hover_after_id = None
        
        self.selected_page.set('')
        self.dropdown_values = []
        self.rune_pages_data = []
        self.default_btn.configure(state='disabled')
        self.delete_btn.configure(state='disabled')
    
    def _update_button_text(self, *args):
        """Update button text with arrow"""
        current_text = self.selected_page.get()
        if not current_text.endswith(" ▼"):
            self.dropdown_button.configure(text=current_text + " ▼")
    
    def _toggle_dropdown(self):
        """Toggle the custom dropdown list"""
        if self.dropdown_open:
            self._close_dropdown()
        else:
            self._open_dropdown()
    
    def _open_dropdown(self):
        """Open the custom dropdown list"""
        if not hasattr(self, 'dropdown_values') or not self.dropdown_values:
            return
        
        self.dropdown_open = True
        
        # Create dropdown list window
        self.dropdown_list = tk.Toplevel(self.dropdown_button.winfo_toplevel())
        self.dropdown_list.wm_overrideredirect(True)
        self.dropdown_list.configure(bg=UIConstants.BACKGROUND_COLOR, relief='solid', bd=1)
        
        # Position below button
        button_x = self.dropdown_button.winfo_rootx()
        button_y = self.dropdown_button.winfo_rooty() + self.dropdown_button.winfo_height()
        button_width = self.dropdown_button.winfo_width()
        
        # Create listbox
        self.listbox = tk.Listbox(
            self.dropdown_list,
            font=('Arial', 11),
            bg=UIConstants.BUTTON_DEFAULT_BG,
            fg=UIConstants.BUTTON_DEFAULT_FG,
            selectbackground=UIConstants.BUTTON_SELECTED_BG,
            selectforeground=UIConstants.BUTTON_SELECTED_FG,
            relief='flat',
            bd=0,
            height=min(6, len(self.dropdown_values)),
            width=25
        )
        self.listbox.pack(fill='both', expand=True)
        
        # Populate listbox
        for value in self.dropdown_values:
            self.listbox.insert(tk.END, value)
        
        # Bind events for tooltips and selection
        self.listbox.bind('<Motion>', self._on_listbox_motion)
        self.listbox.bind('<Leave>', self._on_listbox_leave)
        self.listbox.bind('<Button-1>', self._on_listbox_click)
        self.listbox.bind('<Double-Button-1>', self._on_listbox_click)
        self.listbox.bind('<Return>', self._on_listbox_click)
        self.listbox.bind('<space>', self._on_listbox_click)
        
        # Position and show
        list_height = min(6, len(self.dropdown_values)) * 20 + 4
        self.dropdown_list.geometry(f"{button_width}x{list_height}+{button_x}+{button_y}")
        
        # Focus without grab to avoid blocking window manager events
        self.listbox.focus_set()
        
        # Bind keyboard events
        self.dropdown_list.bind('<Escape>', self._on_escape_key)
        self.dropdown_list.bind('<KeyPress>', self._on_dropdown_keypress)
        
        # Set up click-outside detection without grab
        self._setup_click_outside_detection()
        
        # Auto-close after a delay if focus is lost (fallback)
        # Commented out to fix single-click issue
        # self.dropdown_list.after(100, self._check_focus_periodically)
    
    def _on_escape_key(self, event):
        """Handle escape key press"""
        self._close_dropdown()
    
    def _on_dropdown_keypress(self, event):
        """Handle keyboard events in the dropdown"""
        # Close dropdown on Escape
        if event.keysym == 'Escape':
            self._close_dropdown()
            return 'break'
        
        # For other keys, just close the dropdown and let the main app handle them
        # This prevents the dropdown from blocking application-level shortcuts
        if event.keysym in ['F4'] and event.state & 0x8:  # Alt+F4
            self._close_dropdown()
            # Don't return 'break' so the event can propagate to close the app
            return
        
        # Allow arrow keys and Enter for navigation within dropdown
        if event.keysym in ['Up', 'Down', 'Return', 'space']:
            return  # Let listbox handle these
        
        # For other keys, close dropdown and don't consume the event
        self._close_dropdown()
    
    def _setup_click_outside_detection(self):
        """Setup click-outside detection without using grab"""
        try:
            # Bind to root window to detect clicks anywhere
            root = self.dropdown_button.winfo_toplevel()
            root.bind_all('<Button-1>', self._on_global_click, add=True)
            self._global_click_bound = True
        except:
            self._global_click_bound = False
    
    def _on_global_click(self, event):
        """Handle global click events to detect clicks outside dropdown"""
        if not self.dropdown_open or not self.dropdown_list:
            return
        
        try:
            # Get click coordinates relative to screen
            click_x = event.x_root
            click_y = event.y_root
            
            # Get dropdown window bounds
            dropdown_x = self.dropdown_list.winfo_rootx()
            dropdown_y = self.dropdown_list.winfo_rooty()
            dropdown_width = self.dropdown_list.winfo_width()
            dropdown_height = self.dropdown_list.winfo_height()
            
            # Get dropdown button bounds
            button_x = self.dropdown_button.winfo_rootx()
            button_y = self.dropdown_button.winfo_rooty()
            button_width = self.dropdown_button.winfo_width()
            button_height = self.dropdown_button.winfo_height()
            
            # Check if click is outside both dropdown and button
            outside_dropdown = not (dropdown_x <= click_x <= dropdown_x + dropdown_width and
                                  dropdown_y <= click_y <= dropdown_y + dropdown_height)
            
            outside_button = not (button_x <= click_x <= button_x + button_width and
                                button_y <= click_y <= button_y + button_height)
            
            if outside_dropdown and outside_button:
                self._close_dropdown()
        except:
            # If detection fails, close dropdown for safety
            self._close_dropdown()
    
    def _check_focus_periodically(self):
        """Periodically check if dropdown should stay open"""
        if not self.dropdown_open or not self.dropdown_list:
            return
        
        try:
            # Check if dropdown or its children have focus
            focused_widget = self.dropdown_button.focus_get()
            if focused_widget is None or not str(focused_widget).startswith(str(self.dropdown_list)):
                # Schedule another check - give some grace time
                self.dropdown_list.after(500, self._check_if_should_close)
            else:
                # Still has focus, check again later
                self.dropdown_list.after(200, self._check_focus_periodically)
        except:
            # If check fails, close dropdown
            self._close_dropdown()
    
    def _check_if_should_close(self):
        """Final check before closing dropdown due to focus loss"""
        if not self.dropdown_open or not self.dropdown_list:
            return
        
        try:
            # More lenient check - see if user is still interacting
            focused_widget = self.dropdown_button.focus_get()
            if focused_widget is None or not (str(focused_widget).startswith(str(self.dropdown_list)) or 
                                            focused_widget == self.dropdown_button):
                self._close_dropdown()
        except:
            self._close_dropdown()
    
    def _close_dropdown(self):
        """Close the custom dropdown list"""
        if self.dropdown_list:
            try:
                # No grab to release since we don't use grab anymore
                self.dropdown_list.destroy()
            except:
                pass
            self.dropdown_list = None
        self.dropdown_open = False
        self._hide_tooltip()
        
        # Clean up global click binding
        self._cleanup_click_detection()
    
    def _cleanup_click_detection(self):
        """Clean up global click detection"""
        try:
            if hasattr(self, '_global_click_bound') and self._global_click_bound:
                root = self.dropdown_button.winfo_toplevel()
                root.unbind_all('<Button-1>')
                self._global_click_bound = False
        except:
            pass
    
    def _on_listbox_click(self, event):
        """Handle listbox item selection"""
        try:
            selection = self.listbox.curselection()
            if selection:
                selected_text = self.listbox.get(selection[0])
                self.selected_page.set(selected_text)
                self._close_dropdown()
                self._on_dropdown_select()
        except:
            pass
    
    def _on_listbox_motion(self, event):
        """Handle mouse motion over listbox items"""
        try:
            index = self.listbox.nearest(event.y)
            
            # Hide previous tooltip
            self._hide_tooltip()
            
            # Cancel any pending tooltip
            if self.hover_after_id:
                self.dropdown_button.after_cancel(self.hover_after_id)
            
            # Schedule new tooltip after delay
            self.hover_after_id = self.dropdown_button.after(100, lambda: self._show_listbox_tooltip(index))
        except:
            pass
    
    def _on_listbox_leave(self, event):
        """Handle mouse leave from listbox"""
        self._hide_tooltip()
        if self.hover_after_id:
            self.dropdown_button.after_cancel(self.hover_after_id)
            self.hover_after_id = None
        
    def _on_dropdown_select(self, event=None):
        """Handle dropdown selection"""
        selected_text = self.selected_page.get()
        if not selected_text or selected_text == 'No saved rune pages':
            return
            
        # Skip if it's the placeholder text
        if not selected_text.strip() or selected_text.endswith(') Saved Runes'):
            return
            
        # Find the selected page data - remove "vs." prefix and "(Default)" suffix
        page_name = selected_text.replace(' (Default)', '')
        if page_name.startswith('vs. '):
            page_name = page_name[4:]  # Remove "vs. " prefix
            
        for page_id, name, primary_tree, secondary_tree, keystone, notes, is_default in self.rune_pages_data:
            if name == page_name:
                if self.on_load_rune_page:
                    self.on_load_rune_page(page_id)
                # Update button text based on default status and enable buttons
                self._update_default_button_text(bool(is_default))
                self.default_btn.configure(state='normal')
                self.delete_btn.configure(state='normal')
                break
    
    def _update_default_button_text(self, is_default: bool):
        """Update the default button text based on current selection"""
        # Always show "Default" - the functionality toggles automatically
        self.default_btn.configure(text="Default")
                
    def _on_set_default(self):
        """Handle set default button click"""
        selected_text = self.selected_page.get()
        if not selected_text or selected_text == 'No saved rune pages':
            return
            
        page_name = selected_text.replace(' (Default)', '')
        if page_name.startswith('vs. '):
            page_name = page_name[4:]  # Remove "vs. " prefix
            
        for page_id, name, primary_tree, secondary_tree, keystone, notes, is_default in self.rune_pages_data:
            if name == page_name:
                if self.on_set_default:
                    self.on_set_default(page_id)
                break
                
    def _on_delete(self):
        """Handle delete button click"""
        selected_text = self.selected_page.get()
        if not selected_text or selected_text == 'No saved rune pages':
            return
            
        page_name = selected_text.replace(' (Default)', '')
        if page_name.startswith('vs. '):
            page_name = page_name[4:]  # Remove "vs. " prefix
            
        for page_id, name, primary_tree, secondary_tree, keystone, notes, is_default in self.rune_pages_data:
            if name == page_name:
                if self.on_delete_rune_page:
                    self.on_delete_rune_page(page_id)
                break
    
    
    def _show_listbox_tooltip(self, index):
        """Show tooltip for a specific item in the dropdown listbox"""
        try:
            if index < 0 or index >= len(self.rune_pages_data):
                return
            
            # Get the page data for the hovered item
            page_data = self.rune_pages_data[index]
            
            # Get detailed rune information
            tooltip_text = self._get_rune_page_tooltip_text(page_data)
            
            # Create tooltip window
            self.tooltip = tk.Toplevel(self.dropdown_button.winfo_toplevel())
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.configure(bg='#2C2C2E', relief='solid', bd=1)
            
            # Create tooltip content
            tooltip_label = tk.Label(
                self.tooltip,
                text=tooltip_text,
                font=('Consolas', 9),
                bg='#2C2C2E',
                fg='#FFFFFF',
                justify='left',
                padx=10,
                pady=8
            )
            tooltip_label.pack()
            
            # Position tooltip next to the listbox
            self._position_listbox_tooltip(index)
        except:
            pass
    
    def _hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except:
                pass
            self.tooltip = None
    
    def _position_listbox_tooltip(self, index):
        """Position tooltip next to the listbox item"""
        if not self.tooltip:
            return
        
        try:
            # Check if listbox still exists and is valid
            if not self.listbox or not self.listbox.winfo_exists():
                # Fallback: position relative to dropdown button
                button_x = self.dropdown_button.winfo_rootx()
                button_y = self.dropdown_button.winfo_rooty()
                button_width = self.dropdown_button.winfo_width()
                tooltip_x = button_x + button_width + 10
                tooltip_y = button_y
                self.tooltip.geometry(f"+{tooltip_x}+{tooltip_y}")
                return
            
            # Ensure widgets are updated
            self.listbox.update_idletasks()
            self.tooltip.update_idletasks()
            
            # Get listbox position and dimensions
            listbox_x = self.listbox.winfo_rootx()
            listbox_y = self.listbox.winfo_rooty()
            listbox_width = self.listbox.winfo_width()
            listbox_height = self.listbox.winfo_height()
            
            # Calculate item position more accurately
            total_items = self.listbox.size()
            if total_items > 0:
                item_height = listbox_height / total_items
                item_y_offset = int(index * item_height)
            else:
                item_y_offset = 0
            
            # Get tooltip dimensions
            tooltip_width = self.tooltip.winfo_reqwidth()
            tooltip_height = self.tooltip.winfo_reqheight()
            
            # Get screen dimensions
            screen_width = self.tooltip.winfo_screenwidth()
            screen_height = self.tooltip.winfo_screenheight()
            
            # Calculate ideal position (to the right of listbox)
            tooltip_x = listbox_x + listbox_width + 5
            tooltip_y = listbox_y + item_y_offset
            
            # Adjust if tooltip would go off screen
            if tooltip_x + tooltip_width > screen_width:
                # Position to the left of listbox instead
                tooltip_x = listbox_x - tooltip_width - 5
            
            if tooltip_y + tooltip_height > screen_height:
                # Position higher if it would go off bottom
                tooltip_y = screen_height - tooltip_height - 10
            
            # Ensure tooltip doesn't go above screen
            if tooltip_y < 0:
                tooltip_y = 10
            
            self.tooltip.geometry(f"+{tooltip_x}+{tooltip_y}")
        except Exception as e:
            # Silent fallback - position next to button instead
            try:
                button_x = self.dropdown_button.winfo_rootx()
                button_y = self.dropdown_button.winfo_rooty()
                button_width = self.dropdown_button.winfo_width()
                tooltip_x = button_x + button_width + 10
                tooltip_y = button_y
                self.tooltip.geometry(f"+{tooltip_x}+{tooltip_y}")
            except:
                pass
    
    def _get_rune_page_tooltip_text(self, page_data):
        """Generate tooltip text for a rune page in the specified format"""
        page_id, name, primary_tree, secondary_tree, keystone, notes, is_default = page_data
        
        # Get detailed rune data if callback is available
        detailed_data = None
        if self.on_get_rune_details:
            detailed_data = self.on_get_rune_details(page_id)
        
        tooltip_lines = []
        
        # Title with matchup name
        tooltip_lines.append(f"{name}")
        if bool(is_default):
            tooltip_lines.append("(Default)")
        tooltip_lines.append("")
        
        if detailed_data and detailed_data.get('primary_runes'):
            # Format as requested:
            # Keystone                    Secondary
            # Row 1 runes                1st rune secondary
            # Row 2 runes                2nd rune secondary  
            # Row 3 runes                
            # AF AF Tenacity
            
            primary_runes = detailed_data.get('primary_runes', {})
            secondary_runes = detailed_data.get('secondary_runes', {})
            stat_shards = detailed_data.get('stat_shards', {})
            keystone = detailed_data.get('keystone', keystone)
            
            # Get secondary runes as a list (only non-None values)
            secondary_list = []
            for row in ['secondary_row1', 'secondary_row2', 'secondary_row3']:
                rune = secondary_runes.get(row)
                if rune is not None:
                    secondary_list.append(rune)
            
            # Header line
            tooltip_lines.append(f"{'Keystone':<25} Secondary")
            tooltip_lines.append(f"{keystone:<25} {secondary_tree}")
            tooltip_lines.append("")
            
            # Primary runes with corresponding secondary runes
            primary_row_names = ['primary_row1', 'primary_row2', 'primary_row3']
            secondary_index = 0
            
            for i, row in enumerate(primary_row_names):
                primary_rune = primary_runes.get(row, '')
                secondary_rune = secondary_list[secondary_index] if secondary_index < len(secondary_list) else ''
                
                if primary_rune:  # Only show if there's a primary rune
                    line = f"{primary_rune:<25} {secondary_rune}"
                    tooltip_lines.append(line)
                    
                    # Only increment secondary index if we used a secondary rune
                    if secondary_rune:
                        secondary_index += 1
            
            # Stat shards line
            offense_shard = stat_shards.get('offense', '')
            flex_shard = stat_shards.get('flex', '')
            defense_shard = stat_shards.get('defense', '')
            
            if offense_shard or flex_shard or defense_shard:
                tooltip_lines.append("")
                shards_line = f"{offense_shard} {flex_shard} {defense_shard}".strip()
                tooltip_lines.append(shards_line)
        else:
            # Fallback to basic info if detailed data not available
            tooltip_lines.append(f"Primary: {primary_tree}")
            tooltip_lines.append(f"Secondary: {secondary_tree}")
            tooltip_lines.append(f"Keystone: {keystone}")
        
        if notes:
            tooltip_lines.append("")
            tooltip_lines.append(f"Notes: {notes}")
        
        return "\n".join(tooltip_lines)
