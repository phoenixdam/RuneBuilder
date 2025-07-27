import tkinter as tk
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database_model import DatabaseModel
from models.champion_model import ChampionModel
from models.rune_page_model import RunePageModel
from models.rune_data_model import RuneDataModel
from views.image_loader import ImageLoader
from views.champion_view import ChampionView
from views.saved_runes_view import SavedRunesView
from views.rune_view import RuneView
from views.save_panel_view import SavePanelView
from views.ui_constants import UIConstants
from .rune_state import RuneState
from .champion_controller import ChampionController
from .saved_runes_controller import SavedRunesController
from .rune_controller import RuneController
from .save_controller import SaveController


class MainController:
    """Main controller that coordinates all MVC components"""
    
    def __init__(self):
        # Initialize root window
        self.root = tk.Tk()
        self.root.title("League of Legends Champion Rune Builder")
        self.root.geometry(f"{UIConstants.WINDOW_WIDTH}x{UIConstants.WINDOW_HEIGHT}")
        self.root.configure(bg=UIConstants.BACKGROUND_COLOR)
        
        # Performance optimizations
        self.root.resizable(True, True)
        self.root.minsize(800, 600)  # Set minimum size
        
        # Add resize rate limiting and performance optimizations
        self._resize_timer = None
        self._is_resizing = False
        self._resize_start_time = 0
        self.root.bind('<Configure>', self._on_window_configure)
        
        # Optimize tkinter performance
        self.root.tk.call('tk', 'scaling', 1.0)  # Disable DPI scaling which can cause lag
        
        # Additional performance settings
        self.root.option_add('*tearOff', False)  # Disable menu tear-off
        
        # Use compound strings for better performance
        self.root.tk.call('namespace', 'import', '::tk::unsupported')
        
        # Disable automatic updates during resize
        self.root.tk.call('set', 'tk_strictMotif', 1)
        
        # Set fixed aspect ratio to prevent excessive recalculations
        self.root.update_idletasks()
        
        # Reduce visual effects that can cause lag
        try:
            self.root.wm_attributes('-alpha', 0.99)  # Slight transparency can help with some graphics drivers
        except:
            pass
        
        # Initialize database
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rune_builder.db')
        self.db_model = DatabaseModel(db_path)
        
        # Initialize models
        self.champion_model = ChampionModel(self.db_model)
        self.rune_page_model = RunePageModel(self.db_model)
        self.rune_data_model = RuneDataModel()
        
        # Initialize shared state
        self.rune_state = RuneState()
        
        # Initialize image loader
        self.image_loader = ImageLoader()
        
        # Setup UI and controllers
        self._setup_ui()
        self._setup_controllers()
        self._connect_controllers()
        
        # Run database optimization in background
        self.root.after(1000, self.db_model.optimize_database_background)
        
    def _setup_ui(self):
        """Setup the complete UI layout with optimized geometry management"""
        # Main container with grid for better performance
        main_frame = tk.Frame(self.root, bg=UIConstants.BACKGROUND_COLOR)
        main_frame.pack(fill='both', expand=True, padx=UIConstants.MAIN_PADDING[0], 
                       pady=UIConstants.MAIN_PADDING[1])
        
        # Create main layout: Left panel | Right area using grid for better performance
        content_frame = tk.Frame(main_frame, bg=UIConstants.BACKGROUND_COLOR)
        content_frame.pack(fill='both', expand=True)
        
        # Configure grid weights for smooth resizing
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=0, minsize=UIConstants.CHAMPION_FRAME_WIDTH + 20)  # Champion panel fixed width
        content_frame.grid_columnconfigure(1, weight=1)  # Right area expandable
        
        # Initialize views with grid instead of pack
        self.champion_view = ChampionView(content_frame, self.image_loader)
        
        # Right area with proper spacing
        right_frame = tk.Frame(content_frame, bg=UIConstants.BACKGROUND_COLOR)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0), pady=0)
        
        self.saved_runes_view = SavedRunesView(right_frame, self.image_loader)
        self.rune_view = RuneView(right_frame, self.image_loader)
        self.save_panel_view = SavePanelView(right_frame)
        
    def _setup_controllers(self):
        """Initialize all controllers"""
        self.champion_controller = ChampionController(
            self.champion_model, self.rune_page_model, 
            self.champion_view, self.rune_state
        )
        
        self.saved_runes_controller = SavedRunesController(
            self.rune_page_model, self.saved_runes_view, self.rune_state
        )
        
        self.rune_controller = RuneController(
            self.rune_data_model, self.rune_view, self.rune_state
        )
        
        self.save_controller = SaveController(
            self.rune_page_model, self.save_panel_view, self.rune_state
        )
        
    def _connect_controllers(self):
        """Connect controllers through callbacks"""
        # When champion is selected, load their rune pages
        self.champion_controller.set_champion_changed_callback(
            self.saved_runes_controller.load_champion_rune_pages
        )
        
        # When rune page is loaded, update rune selection
        self.saved_runes_controller.set_rune_page_loaded_callback(
            self.rune_controller.load_rune_page_data
        )
        
        # When runes are cleared or saved, refresh displays
        self.save_controller.set_callbacks(
            on_runes_cleared=self.rune_controller.clear_all_runes,
            on_rune_page_saved=self._on_rune_page_saved
        )
        
    def _on_rune_page_saved(self):
        """Handle when a rune page is saved - refresh the saved runes display"""
        if self.rune_state.selected_champion:
            self.saved_runes_controller.load_champion_rune_pages(
                self.rune_state.selected_champion['id']
            )
            
    def initialize(self):
        """Initialize the application"""
        # Initialize all controllers
        self.champion_controller.initialize()
        self.rune_controller.initialize()
        
    def _on_window_configure(self, event):
        """Handle window resize events with aggressive performance optimizations"""
        # Only handle main window resize events, not child widgets
        if event.widget != self.root:
            return
            
        import time
        current_time = time.time()
        
        # Mark resize start
        if not self._is_resizing:
            self._is_resizing = True
            self._resize_start_time = current_time
            self._disable_performance_heavy_features()
            
        # Cancel previous timer if it exists
        if self._resize_timer:
            self.root.after_cancel(self._resize_timer)
        
        # Set a new timer to handle resize after a longer delay during active resizing
        delay = 200 if self._is_resizing else 50
        self._resize_timer = self.root.after(delay, self._handle_resize)
    
    def _disable_performance_heavy_features(self):
        """Temporarily disable performance-heavy features during resize"""
        # Disable tooltips during resize
        if hasattr(self, 'rune_view'):
            self.rune_view._tooltips_enabled = False
            
        # Suspend widget updates
        try:
            self.root.tk.call('tk', 'busy', 'hold', self.root)
        except:
            pass
    
    def _enable_performance_heavy_features(self):
        """Re-enable performance-heavy features after resize"""
        # Re-enable tooltips
        if hasattr(self, 'rune_view'):
            self.rune_view._tooltips_enabled = True
            
        # Resume widget updates
        try:
            self.root.tk.call('tk', 'busy', 'forget', self.root)
        except:
            pass
    
    def _handle_resize(self):
        """Handle the actual resize operations"""
        import time
        
        # Reset timer
        self._resize_timer = None
        
        # Check if we should end resize mode
        if self._is_resizing and (time.time() - self._resize_start_time) > 0.5:
            self._is_resizing = False
            self._enable_performance_heavy_features()
        
        # Minimal update during resize
        if not self._is_resizing:
            self.root.update_idletasks()
    
    def run(self):
        """Start the application"""
        self.initialize()
        self.root.mainloop()