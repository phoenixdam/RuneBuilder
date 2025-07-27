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
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup saved runes panel UI"""
        saved_container = tk.Frame(self.parent, bg=UIConstants.BACKGROUND_COLOR)
        saved_container.pack(fill='x', pady=UIConstants.SAVED_RUNES_PADDING)
        
        # Scrollable horizontal list for saved runes
        self.canvas = tk.Canvas(saved_container, bg=UIConstants.BACKGROUND_COLOR, 
                              height=UIConstants.SAVED_RUNES_CANVAS_HEIGHT, highlightthickness=0)
        
        # Style horizontal scrollbar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("SavedRunes.Horizontal.TScrollbar", 
                       background=UIConstants.SCROLLBAR_BG, 
                       troughcolor=UIConstants.SCROLLBAR_BG,
                       bordercolor=UIConstants.SCROLLBAR_BORDER, 
                       arrowcolor=UIConstants.SCROLLBAR_ARROW, 
                       darkcolor=UIConstants.SCROLLBAR_BORDER,
                       lightcolor=UIConstants.SCROLLBAR_BG)
        
        self.scrollbar_h = ttk.Scrollbar(saved_container, orient="horizontal", command=self.canvas.xview,
                                       style="SavedRunes.Horizontal.TScrollbar")
        self.saved_runes_frame = tk.Frame(self.canvas, bg=UIConstants.BACKGROUND_COLOR)
        
        self.saved_runes_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.saved_runes_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scrollbar_h.set)
        
        self.canvas.pack(fill="x", expand=True)
        self.scrollbar_h.pack(fill="x")
        
    def set_callbacks(self, on_load: Callable, on_set_default: Callable, on_delete: Callable):
        """Set callbacks for rune page operations"""
        self.on_load_rune_page = on_load
        self.on_set_default = on_set_default
        self.on_delete_rune_page = on_delete
        
    def display_rune_pages(self, rune_pages: List[Tuple]):
        """Display saved rune pages"""
        # Clear existing displays
        for widget in self.saved_runes_frame.winfo_children():
            widget.destroy()
            
        # Display each rune page
        for page_id, name, primary_tree, secondary_tree, keystone, notes, is_default in rune_pages:
            self._create_rune_page_box(page_id, name, keystone, notes, bool(is_default))
            
        # Update canvas scroll region
        self.parent.after_idle(self._update_scroll_region)
        
    def _create_rune_page_box(self, page_id: int, name: str, keystone: str, notes: str, is_default: bool):
        """Create a visual box for a saved rune page"""
        box_frame = tk.Frame(self.saved_runes_frame, relief='raised', 
                            bd=UIConstants.BORDER_WIDTH, 
                            bg=UIConstants.DEFAULT_RUNE_PAGE_BG if is_default else UIConstants.BACKGROUND_COLOR)
        box_frame.pack(side='left', padx=UIConstants.RUNE_PAGE_BOX_PADDING[0], 
                      pady=UIConstants.RUNE_PAGE_BOX_PADDING[1])
        
        # Keystone icon as button
        icon_label = None
        if keystone:
            keystone_icon = self.image_loader.load_rune_image(keystone, size=UIConstants.RUNE_PAGE_ICON_SIZE)
            icon_label = tk.Button(box_frame, image=keystone_icon, bg=box_frame['bg'],
                                  bd=0, relief='flat', activebackground=UIConstants.BUTTON_SYSTEM_BG)
            icon_label.image = keystone_icon
            icon_label.pack(pady=UIConstants.ICON_PADDING)
        
        # Delete button
        delete_btn = tk.Button(box_frame, text="×", 
                              font=('Arial', UIConstants.FONT_SIZE_DELETE_BUTTON, 'bold'),
                              fg=UIConstants.DELETE_BUTTON_FG, bg=box_frame['bg'], bd=0,
                              width=UIConstants.DELETE_BUTTON_SIZE[0], 
                              height=UIConstants.DELETE_BUTTON_SIZE[1],
                              activebackground=UIConstants.BUTTON_SYSTEM_BG,
                              command=lambda: self._on_delete_clicked(page_id))
        delete_btn.pack(pady=UIConstants.DELETE_BUTTON_PADDING)
            
        # Bind click events
        def on_click(event=None):
            if self.on_load_rune_page:
                self.on_load_rune_page(page_id)
        
        def on_double_click(event=None):
            if self.on_set_default:
                self.on_set_default(page_id)
        
        # Bind to all widgets
        box_frame.bind("<Button-1>", on_click)
        box_frame.bind("<Double-Button-1>", on_double_click)
        
        if icon_label:
            icon_label.configure(command=lambda: on_click())
            icon_label.bind("<Double-Button-1>", on_double_click)
        
        # Prevent delete button from propagating clicks
        delete_btn.bind("<Button-1>", lambda e: "break")
            
        # Tooltip
        tooltip_text = name
        if notes and notes.strip():
            tooltip_text += f"\n{notes.strip()}"
        
        all_widgets = [box_frame, delete_btn]
        if icon_label:
            all_widgets.append(icon_label)
        
        for widget in all_widgets:
            self._create_tooltip(widget, tooltip_text)
            
    def _on_delete_clicked(self, page_id: int):
        """Handle delete button click"""
        if self.on_delete_rune_page:
            self.on_delete_rune_page(page_id)
            
    def _create_tooltip(self, widget: tk.Widget, text: str):
        """Create a tooltip for a widget"""
        def on_enter(event):
            cleanup_tooltip()
                
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tooltip.configure(bg=UIConstants.TOOLTIP_BG)
            label = tk.Label(tooltip, text=text, background=UIConstants.TOOLTIP_BG,
                           font=('Arial', 11), relief='solid', borderwidth=1,
                           fg=UIConstants.BACKGROUND_COLOR, justify='left')
            label.pack()
            widget.tooltip = tooltip
            
        def cleanup_tooltip():
            if hasattr(widget, 'tooltip') and widget.tooltip:
                try:
                    widget.tooltip.destroy()
                except:
                    pass
                widget.tooltip = None
                
        def on_leave(event):
            cleanup_tooltip()
                
        # Initialize tooltip attribute
        widget.tooltip = None
        
        # Bind events
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", lambda e: cleanup_tooltip())
        widget.bind("<FocusOut>", lambda e: cleanup_tooltip())
        
    def _update_scroll_region(self):
        """Update canvas scroll region"""
        self.saved_runes_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))