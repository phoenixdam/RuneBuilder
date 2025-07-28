import tkinter as tk
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database_model import DatabaseModel
from models.champion_model import ChampionModel
from models.rune_page_model import RunePageModel
from models.rune_data_model import RuneDataModel
from models.profile_model import ProfileModel
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
        
        # Set application icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'phoenix_logo.png')
            self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Keep window creation simple
        
        # Simple window setup
        self.root.resizable(True, True)
        self.root.minsize(800, 720)
        
        # Initialize database
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rune_builder.db')
        self.db_model = DatabaseModel(db_path)
        
        # Initialize models
        self.champion_model = ChampionModel(self.db_model)
        self.rune_page_model = RunePageModel(self.db_model)
        self.rune_data_model = RuneDataModel()
        self.profile_model = ProfileModel(self.db_model)
        
        # Initialize shared state
        self.rune_state = RuneState()
        
        # Initialize image loader
        self.image_loader = ImageLoader()
        
        # Setup UI and controllers
        self._setup_ui()
        self._setup_controllers()
        self._connect_controllers()
        
        # Database is ready
        
    def _setup_ui(self):
        """Setup the complete UI layout with optimized geometry management"""
        # Main container with grid for better performance
        main_frame = tk.Frame(self.root, bg=UIConstants.BACKGROUND_COLOR)
        main_frame.pack(fill='both', expand=True, padx=UIConstants.MAIN_PADDING[0], 
                       pady=UIConstants.MAIN_PADDING[1])
        
        # Create main layout: Top row for champions | Bottom area for runes
        content_frame = tk.Frame(main_frame, bg=UIConstants.BACKGROUND_COLOR)
        content_frame.pack(fill='both', expand=True)
        
        # Configure grid weights for smooth resizing
        content_frame.grid_rowconfigure(0, weight=0)  # Champion row fixed height
        content_frame.grid_rowconfigure(1, weight=1)  # Rune area expandable
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Top row for champion selection
        champion_container = tk.Frame(content_frame, bg=UIConstants.BACKGROUND_COLOR)
        champion_container.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # Initialize champion view in top row
        self.champion_view = ChampionView(champion_container, self.image_loader)
        
        # Bottom area for runes and saved pages
        main_rune_frame = tk.Frame(content_frame, bg=UIConstants.BACKGROUND_COLOR)
        main_rune_frame.grid(row=1, column=0, sticky='nsew')
        
        # Configure main rune frame layout
        main_rune_frame.grid_rowconfigure(0, weight=0)  # Saved runes dropdown
        main_rune_frame.grid_rowconfigure(1, weight=1)  # Rune selection area
        main_rune_frame.grid_rowconfigure(2, weight=0)  # Save panel
        main_rune_frame.grid_columnconfigure(0, weight=1)
        
        # Create containers for each section
        saved_container = tk.Frame(main_rune_frame, bg=UIConstants.BACKGROUND_COLOR)
        saved_container.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        rune_container = tk.Frame(main_rune_frame, bg=UIConstants.BACKGROUND_COLOR)
        rune_container.grid(row=1, column=0, sticky='nsew')
        
        save_container = tk.Frame(main_rune_frame, bg=UIConstants.BACKGROUND_COLOR)
        save_container.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        
        # Initialize views in their respective containers
        self.saved_runes_view = SavedRunesView(saved_container, self.image_loader)
        self.rune_view = RuneView(rune_container, self.image_loader)
        self.save_panel_view = SavePanelView(save_container)
        
    def _setup_controllers(self):
        """Initialize all controllers"""
        self.champion_controller = ChampionController(
            self.champion_model, self.rune_page_model, 
            self.champion_view, self.rune_state,
            self.profile_model, self.image_loader
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
        # When champion is selected, load their rune pages and update matchup autocomplete
        self.champion_controller.set_champion_changed_callback(
            self._on_champion_changed
        )
        
        # When rune page is loaded, update rune selection and save panel
        self.saved_runes_controller.set_rune_page_loaded_callback(
            self._on_rune_page_loaded
        )
        
        # When rune page is deleted, refresh champion list
        self.saved_runes_controller.set_rune_page_deleted_callback(
            self._on_rune_page_deleted
        )
        
        # When runes are cleared or saved, refresh displays
        self.save_controller.set_callbacks(
            on_runes_cleared=self._on_runes_cleared,
            on_rune_page_saved=self._on_rune_page_saved
        )
        
        # Populate champion names for matchup autocomplete
        self._populate_champion_names()
        
    def _on_rune_page_loaded(self, data: dict):
        """Handle when a rune page is loaded - update both rune selection and save panel"""
        # Load rune data into the rune controller
        self.rune_controller.load_rune_page_data(data)
        
        # Load rune page data into save panel for editing
        self.save_controller.load_rune_page_data_to_panel(data)
    
    def _on_runes_cleared(self):
        """Handle when runes are cleared - clear rune selection and exit edit mode"""
        self.rune_controller.clear_all_runes()
        self.save_controller.clear_edit_mode()
        # Also clear the saved runes dropdown selection
        self.saved_runes_view.clear_selection()
    
    def _on_rune_page_saved(self):
        """Handle when a rune page is saved - refresh the saved runes display and champion list"""
        if self.rune_state.selected_champion:
            # Get the saved matchup name to select it in the dropdown
            saved_name = self.save_controller.save_panel_view.get_rune_page_name()
            if not saved_name:
                saved_name = "Generic"  # Handle empty name case
            
            self.saved_runes_controller.load_champion_rune_pages(
                self.rune_state.selected_champion['id']
            )
            
            # Select the newly saved rune page in the dropdown
            self.saved_runes_controller.select_rune_page_by_name(saved_name)
            
            # Also refresh champion list to update counts
            self.champion_controller.refresh_champions()
            
    def _on_rune_page_deleted(self):
        """Handle when a rune page is deleted - refresh champion list"""
        self.champion_controller.refresh_champions()
    
    def _on_champion_changed(self, champion_id: int):
        """Handle when champion selection changes"""
        # Load their rune pages (or clear if champion_id is None)
        self.saved_runes_controller.load_champion_rune_pages(champion_id)
        
        # Update matchup autocomplete to exclude selected champion
        self._populate_champion_names()
            
    def initialize(self):
        """Initialize the application"""
        # Initialize all controllers
        self.champion_controller.initialize()
        self.rune_controller.initialize()
        
    
    def _populate_champion_names(self):
        """Populate champion names for the matchup autocomplete, excluding selected champion"""
        try:
            # Get all champion names from the database
            champions_data = self.champion_model.get_champions_with_rune_counts()
            champion_names = [name for _, name, _, _ in champions_data]
            
            # Exclude the currently selected champion
            if self.rune_state.selected_champion:
                selected_name = self.rune_state.selected_champion['name']
                champion_names = [name for name in champion_names if name != selected_name]
            
            self.save_controller.set_champion_names(champion_names)
        except Exception:
            # If there's an error, provide a fallback empty list
            self.save_controller.set_champion_names([])
    
    def run(self):
        """Start the application"""
        self.initialize()
        self.root.mainloop()