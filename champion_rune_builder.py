import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import json
import os
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
import glob

class UIConstants:
    # Main window
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 700
    
    # Champion display
    CHAMPION_IMAGE_SIZE = (40, 40)
    CHAMPION_BUTTON_SIZE = (45, 45)
    CHAMPION_CANVAS_WIDTH = 52
    CHAMPION_FRAME_WIDTH = 80
    CHAMPION_BUTTON_PADDING = 2
    
    # Rune tree selection
    TREE_ICON_SIZE = (24, 24)
    TREE_ICON_DISPLAY_SIZE = (32, 32)
    TREE_BUTTON_SIZE = (80, 55)
    TREE_BUTTON_PADDING = 2
    TREE_BUTTON_WRAP_LENGTH = 75
    
    # Keystone runes
    KEYSTONE_IMAGE_SIZE = (48, 48)
    KEYSTONE_BUTTON_SIZE = (110, 95)
    KEYSTONE_BUTTON_PADDING = (3, 1)
    KEYSTONE_WRAP_LENGTH = 105
    
    # Primary runes
    PRIMARY_RUNE_IMAGE_SIZE = (32, 32)
    PRIMARY_RUNE_BUTTON_SIZE = (90, 75)
    PRIMARY_RUNE_PADDING = (2, 2)
    PRIMARY_RUNE_WRAP_LENGTH = 85
    
    # Secondary runes
    SECONDARY_RUNE_IMAGE_SIZE = (28, 28)
    SECONDARY_RUNE_BUTTON_SIZE = (100, 60)
    SECONDARY_RUNE_PADDING = 1
    SECONDARY_RUNE_WRAP_LENGTH = 100
    
    # Stat shards
    STAT_SHARD_IMAGE_SIZE = (20, 20)
    STAT_SHARD_BUTTON_SIZE = (100, 60)
    STAT_SHARD_PADDING = 1
    STAT_SHARD_WRAP_LENGTH = 100
    
    # Saved rune pages
    RUNE_PAGE_ICON_SIZE = (32, 32)
    SAVED_RUNES_CANVAS_HEIGHT = 80
    SAVED_RUNES_PADDING = (0, 4)
    RUNE_PAGE_BOX_PADDING = (5, 5)
    RUNE_PAGE_NAME_WRAP_LENGTH = 60
    RUNE_PAGE_NAME_MAX_LENGTH = 12
    
    # Layout and spacing
    MAIN_PADDING = (4, 2)
    CONTENT_PADDING = (8, 4)
    DELETE_BUTTON_PADDING = (5, 0)
    ICON_PADDING = 2
    
    # Form inputs
    INPUT_FIELD_WIDTH = 32
    LABEL_WIDTH = 15
    DELETE_BUTTON_SIZE = (2, 1)
    
    # Text display
    RUNE_PLACEHOLDER_TEXT_LENGTH = 8
    
    # Visual styling
    BORDER_WIDTH = 2
    RAISED_BORDER = 2
    SUNKEN_BORDER = 2
    
    # Typography
    FONT_SIZE_DEFAULT = 11
    FONT_SIZE_TREE_BUTTON = 10
    FONT_SIZE_KEYSTONE_HEADER = 12
    FONT_SIZE_DELETE_BUTTON = 8
    
    # Color scheme
    BACKGROUND_COLOR = 'white'
    TEXT_COLOR = '#2c3e50'
    PLACEHOLDER_COLOR = '#3C3C41'
    
    # Button colors
    BUTTON_DEFAULT_BG = '#3C3C41'
    BUTTON_DEFAULT_FG = 'white'
    BUTTON_SELECTED_BG = '#C8AA6E'
    BUTTON_SELECTED_FG = 'black'
    BUTTON_SYSTEM_BG = 'SystemButtonFace'
    DELETE_BUTTON_FG = 'red'
    
    # Special highlights
    DEFAULT_RUNE_PAGE_BG = '#C8AA6E'
    CHAMPION_SELECTED_BG = 'lightblue'
    TOOLTIP_BG = 'lightyellow'
    
    # Scrollbar styling
    SCROLLBAR_BG = '#ecf0f1'
    SCROLLBAR_BORDER = '#bdc3c7'
    SCROLLBAR_ARROW = '#7f8c8d'
    
    # Database performance
    DB_CACHE_SIZE = 10000
    DB_MMAP_SIZE = 268435456  # 256MB

class ChampionRuneBuilder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("League of Legends Champion Rune Builder")
        self.root.geometry(f"{UIConstants.WINDOW_WIDTH}x{UIConstants.WINDOW_HEIGHT}")
        self.root.configure(bg=UIConstants.BACKGROUND_COLOR)
        
        # Database setup
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rune_builder.db')
        self.init_database()
        
        # Run database optimization on startup (in background)
        self.root.after(1000, self.optimize_database_background)
        
        # Current state
        self.selected_champion = None
        self.selected_primary_tree = None
        self.selected_secondary_tree = None
        self.selected_runes = {
            'keystone': None,
            'primary_row1': None,
            'primary_row2': None,
            'primary_row3': None,
            'secondary_row1': None,
            'secondary_row2': None,
            'stat_shards': {'offense': None, 'flex': None, 'defense': None}
        }
        
        # Store button references for visual feedback
        self.rune_buttons = {}
        self.stat_buttons = {}
        self.champion_buttons = {}
        
        # Track order of secondary rune selections for FIFO logic
        self.secondary_rune_selection_order = []
        
        # Image cache for performance
        self.image_cache = {}
        
        # Pre-built rune tree widgets to eliminate flickering
        self.primary_tree_widgets = {}
        self.secondary_tree_widgets = {}
        self.cached_rune_buttons = {}
        
        # Define rune trees and their runes (matching actual files)
        self.rune_trees = {
            'Precision': {
                'color': '#C8AA6E',
                'keystones': ['Press the Attack', 'Lethal Tempo', 'Fleet Footwork', 'Conqueror'],
                'row1': ['Absorb Life', 'Triumph', 'Presence of Mind'],
                'row2': ['Legend: Alacrity', 'Legend: Haste', 'Legend: Bloodline'],
                'row3': ['Coup de Grace', 'Cut Down', 'Last Stand']
            },
            'Domination': {
                'color': '#C83E3A',
                'keystones': ['Electrocute', 'Dark Harvest', 'Hail of Blades'],
                'row1': ['Cheap Shot', 'Taste of Blood', 'Sudden Impact'],
                'row2': ['Sixth Sense', 'Grisly Mementos', 'Deep Ward'],
                'row3': ['Treasure Hunter', 'Relentless Hunter', 'Ultimate Hunter']
            },
            'Sorcery': {
                'color': '#6AA0CB',
                'keystones': ['Summon Aery', 'Arcane Comet', 'Phase Rush'],
                'row1': ['Axiom Arcanist', 'Manaflow Band', 'Nimbus Cloak'],
                'row2': ['Transcendence', 'Celerity', 'Absolute Focus'],
                'row3': ['Scorch', 'Waterwalking', 'Gathering Storm']
            },
            'Resolve': {
                'color': '#A1D586',
                'keystones': ['Grasp of the Undying', 'Aftershock', 'Guardian'],
                'row1': ['Demolish', 'Font of Life', 'Shield Bash'],
                'row2': ['Conditioning', 'Second Wind', 'Bone Plating'],
                'row3': ['Overgrowth', 'Revitalize', 'Unflinching']
            },
            'Inspiration': {
                'color': '#C0C0C0',
                'keystones': ['Glacial Augment', 'Unsealed Spellbook', 'First Strike'],
                'row1': ['Hextech Flashtraption', 'Magical Footwear', 'Cash Back'],
                'row2': ['Triple Tonic', 'Time Warp Tonic', 'Biscuit Delivery'],
                'row3': ['Cosmic Insight', 'Approach Velocity', 'Jack of All Trades']
            }
        }
        
        # Stat shards (based on actual files found)
        self.stat_shards = {
            'offense': ['Adaptive Force', 'Attack Speed', 'Ability Haste'],
            'flex': ['Adaptive Force', 'Movement Speed', 'Health Scaling'],
            'defense': ['Health', 'Health Scaling', 'Tenacity and Slow Resist']
        }
        
        self.setup_ui()
        self.populate_champions()
        self.preload_all_rune_widgets()
        
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create champions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS champions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                image_path TEXT NOT NULL
            )
        ''')
        
        # Create rune_pages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rune_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                champion_id INTEGER,
                primary_tree TEXT,
                secondary_tree TEXT,
                keystone TEXT,
                primary_runes TEXT,
                secondary_runes TEXT,
                stat_shards TEXT,
                notes TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (champion_id) REFERENCES champions (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_champion_name ON champions(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_champion_id ON rune_pages(champion_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_name ON rune_pages(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_default ON rune_pages(is_default)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_primary_tree ON rune_pages(primary_tree)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_secondary_tree ON rune_pages(secondary_tree)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rune_pages_created_date ON rune_pages(created_date)')
        
        # Composite indexes for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_champion_rune_pages ON rune_pages(champion_id, is_default)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tree_combination ON rune_pages(primary_tree, secondary_tree)')
        
        # Optimize database for better performance
        cursor.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging for better concurrency
        cursor.execute('PRAGMA synchronous=NORMAL')  # Faster writes
        cursor.execute(f'PRAGMA cache_size={UIConstants.DB_CACHE_SIZE}')  # Larger cache
        cursor.execute('PRAGMA temp_store=MEMORY')  # Use memory for temp tables
        cursor.execute(f'PRAGMA mmap_size={UIConstants.DB_MMAP_SIZE}')  # Memory-mapped I/O
        
        conn.commit()
        conn.close()
        
    def optimize_database(self):
        """Run database optimization commands"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze tables to update statistics for better query planning
        cursor.execute('ANALYZE')
        
        # Vacuum to reclaim space and defragment
        cursor.execute('VACUUM')
        
        conn.commit()
        conn.close()
    
    def optimize_database_background(self):
        """Run database optimization in background thread"""
        import threading
        def optimize():
            try:
                self.optimize_database()
            except Exception as e:
                pass  # Database optimization failed silently
        
        thread = threading.Thread(target=optimize, daemon=True)
        thread.start()
        
    def populate_champions(self):
        """Populate champions table from existing champion images"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        champions_dir = os.path.join(script_dir, 'champions_files', '42px')
        
        if not os.path.exists(champions_dir):
            pass  # Champions directory not found
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing champions to avoid duplicates
        cursor.execute("SELECT name FROM champions")
        existing_champions = {row[0] for row in cursor.fetchall()}
        
        # Process all champion image files
        for filename in os.listdir(champions_dir):
            if filename.endswith('.png') and filename.startswith('42px-'):
                # Extract champion name from filename
                # Format: 42px-Champion_Name_OriginalSquare.png
                name_part = filename[5:-4]  # Remove "42px-" and ".png"
                if name_part.endswith('_OriginalSquare'):
                    champion_name = name_part[:-14]  # Remove "_OriginalSquare"
                    champion_name = champion_name.replace('_', ' ')
                    champion_name = self._normalize_champion_name(champion_name)
                        
                    if champion_name not in existing_champions:
                        image_path = os.path.join(champions_dir, filename)
                        cursor.execute(
                            "INSERT INTO champions (name, image_path) VALUES (?, ?)",
                            (champion_name, image_path)
                        )
        
        conn.commit()
        conn.close()
        pass  # Champions database populated successfully
    
    def _normalize_champion_name(self, champion_name):
        CHAMPION_NAME_FIXES = {
            "Cho'Gath": "Cho'Gath", "Dr. Mundo": "Dr. Mundo", "Jarvan IV": "Jarvan IV",
            "Master Yi": "Master Yi", "Miss Fortune": "Miss Fortune", "Aurelion Sol": "Aurelion Sol",
            "Lee Sin": "Lee Sin", "Twisted Fate": "Twisted Fate", "Xin Zhao": "Xin Zhao",
            "Renata Glasc": "Renata Glasc"
        }
        return CHAMPION_NAME_FIXES.get(champion_name, champion_name)
    
    def _load_image_with_fallback(self, path_patterns, size, cache_prefix, placeholder_text="", placeholder_color=UIConstants.PLACEHOLDER_COLOR):
        """Unified image loading with fallback and caching"""
        cache_key = f"{cache_prefix}_{hash(str(path_patterns))}_{size}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
            
        # Try to load from each possible path
        for path in path_patterns:
            try:
                if os.path.exists(path):
                    img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[cache_key] = photo
                    return photo
            except Exception:
                continue
        
        # Create placeholder if no image found
        photo = self.create_placeholder_image(size, color=placeholder_color, text=placeholder_text)
        self.image_cache[cache_key] = photo
        return photo
        
    def load_champion_image(self, image_path, size=UIConstants.CHAMPION_IMAGE_SIZE):
        """Load champion image with fallback and caching"""
        return self._load_image_with_fallback([image_path], size, "champion", "?")
        
    def create_placeholder_image(self, size, color=UIConstants.PLACEHOLDER_COLOR, text=''):
        """Create a placeholder image for runes"""
        img = Image.new('RGBA', size, color)
        draw = ImageDraw.Draw(img)
        
        if text:
            try:
                bbox = draw.textbbox((0, 0), text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (size[0] - text_width) // 2
                y = (size[1] - text_height) // 2
                draw.text((x, y), text, fill=UIConstants.BUTTON_DEFAULT_FG)
            except:
                draw.text((5, 5), text, fill=UIConstants.BUTTON_DEFAULT_FG)
        
        return ImageTk.PhotoImage(img)
    
    def load_rune_image(self, rune_name, size=(64, 64)):
        """Load a rune image from the file system or create placeholder with caching"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rune_name_clean = rune_name.replace(" ", "_").replace("'", "").replace(":", "-")
        
        possible_paths = [
            os.path.join(script_dir, 'runes_files', 'runes', f'52px-{rune_name_clean}_rune.png'),
            os.path.join(script_dir, 'runes_files', 'runes', f'52px-{rune_name.replace(" ", "_")}_rune.png'),
            os.path.join(script_dir, 'runes_files', 'runes', f'{rune_name_clean}.png'),
            os.path.join(script_dir, 'runes_files', 'runes', f'{rune_name}.png'),
        ]
        
        return self._load_image_with_fallback(possible_paths, size, "rune", rune_name[:UIConstants.RUNE_PLACEHOLDER_TEXT_LENGTH])
    
    def load_tree_icon(self, tree_name, size=UIConstants.TREE_ICON_DISPLAY_SIZE):
        """Load a tree icon or create placeholder"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        possible_paths = [
            os.path.join(script_dir, 'runes_files', 'runes', f'52px-{tree_name}_icon.png'),
            os.path.join(script_dir, 'runes_files', f'{tree_name}_icon.png'),
            os.path.join(script_dir, 'icons', f'52px-{tree_name}_icon.png'),
            os.path.join(script_dir, 'icons', f'{tree_name}_icon.png'),
        ]
        
        tree_data = self.rune_trees.get(tree_name, {'color': '#3C3C41'})
        return self._load_image_with_fallback(possible_paths, size, "tree", tree_name[:4], tree_data['color'])
    
    def load_stat_shard_image(self, shard_name, size=UIConstants.STAT_SHARD_IMAGE_SIZE):
        """Load a stat shard image or create placeholder with caching"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        shard_mapping = {
            'Adaptive Force': 'Adaptive_Force', 'Attack Speed': 'Attack_Speed', 'Ability Haste': 'Ability_Haste',
            'Armor': 'Armor', 'Magic Resist': 'Magic_Resist', 'Health': 'Health',
            'Movement Speed': 'Movement_Speed', 'Health Scaling': 'Health_Scaling',
            'Tenacity and Slow Resist': 'Tenacity_and_Slow_Resist'
        }
        
        file_name = shard_mapping.get(shard_name, shard_name.replace(' ', '_'))
        possible_paths = [
            os.path.join(script_dir, 'runes_files', 'shards', f'30px-Rune_shard_{file_name}.png'),
            os.path.join(script_dir, 'runes_files', 'Rune Shard', f'{file_name}.png'),
            os.path.join(script_dir, 'runes_files', f'{file_name}.png'),
        ]
        
        color = self._get_stat_shard_color(shard_name)
            
        return self._load_image_with_fallback(possible_paths, size, "shard", shard_name[:3], color)
    
    def _get_stat_shard_color(self, shard_name):
        SHARD_COLORS = {
            'offense': '#C83E3A',
            'flex': '#C8AA6E', 
            'defense': '#A1D586'
        }
        
        OFFENSE_KEYWORDS = ['Force', 'Speed', 'Haste']
        FLEX_KEYWORDS = ['Armor', 'Resist']
        
        if any(keyword in shard_name for keyword in OFFENSE_KEYWORDS):
            return SHARD_COLORS['offense']
        elif any(keyword in shard_name for keyword in FLEX_KEYWORDS):
            return SHARD_COLORS['flex']
        else:
            return SHARD_COLORS['defense']
    
    def preload_all_rune_widgets(self):
        """Pre-create all rune tree widgets to eliminate flickering"""
        # Pre-create primary tree widgets
        for tree_name in self.rune_trees.keys():
            primary_widget = tk.Frame(self.primary_runes_frame, bg='white')
            self._build_primary_tree_content(primary_widget, tree_name)
            self.primary_tree_widgets[tree_name] = primary_widget
            
            secondary_widget = tk.Frame(self.secondary_runes_frame, bg='white')
            self._build_secondary_tree_content(secondary_widget, tree_name)
            self.secondary_tree_widgets[tree_name] = secondary_widget
    
    def _build_primary_tree_content(self, parent_widget, tree_name):
        """Build primary tree content in the specified widget"""
        tree_data = self.rune_trees[tree_name]
        
        # Store buttons for this tree
        tree_buttons = {}
        
        # Keystones
        keystone_label = tk.Label(parent_widget, text="KEYSTONES",
                                 font=('Arial', 12, 'bold'), fg=tree_data['color'],
                                 bg='white')
        keystone_label.pack(pady=(0, 10))
        
        keystone_frame = tk.Frame(parent_widget, bg='white')
        keystone_frame.pack(pady=(0, 20))
        
        for i, keystone in enumerate(tree_data['keystones']):
            rune_image = self.load_rune_image(keystone, size=(48, 48))
            config = {'width': 55, 'height': 55}
            btn = self._create_rune_button(keystone_frame, keystone, rune_image, config,
                                         lambda k=keystone: self.select_rune('keystone', k))
            btn.grid(row=0, column=i, padx=3, pady=1)
            tree_buttons[('keystone', keystone)] = btn
        
        # Other rows
        rows = ['row1', 'row2', 'row3']
        for row in rows:
            row_frame = tk.Frame(parent_widget, bg='white')
            row_frame.pack(pady=(5, 5))
            
            for j, rune in enumerate(tree_data[row]):
                rune_image = self.load_rune_image(rune, size=(32, 32))
                config = {'width': 40, 'height': 40}
                btn = self._create_rune_button(row_frame, rune, rune_image, config,
                                             lambda r=f'primary_{row}', rn=rune: self.select_rune(r, rn))
                btn.grid(row=0, column=j, padx=2)
                tree_buttons[(f'primary_{row}', rune)] = btn
        
        # Cache buttons for this tree
        self.cached_rune_buttons[f'primary_{tree_name}'] = tree_buttons
    
    def _build_secondary_tree_content(self, parent_widget, tree_name):
        """Build secondary tree content in the specified widget"""
        tree_data = self.rune_trees[tree_name]
        
        # Store buttons for this tree
        tree_buttons = {}
        
        # Secondary tree label
        label = tk.Label(parent_widget, text=tree_name,
                        font=('Arial', 12, 'bold'), fg=tree_data['color'],
                        bg='white')
        label.pack(pady=(0, 10))
        
        # Only show rows 1-3 for secondary tree
        rows = ['row1', 'row2', 'row3']
        for row in rows:
            row_frame = tk.Frame(parent_widget, bg='white')
            row_frame.pack(pady=5)
            
            for j, rune in enumerate(tree_data[row]):
                rune_image = self.load_rune_image(rune, size=(28, 28))
                config = {'width': 35, 'height': 35}
                btn = self._create_rune_button(row_frame, rune, rune_image, config,
                                             lambda r=f'secondary_{row}', rn=rune: self.select_rune(r, rn))
                btn.grid(row=0, column=j, padx=1)
                tree_buttons[(f'secondary_{row}', rune)] = btn
        
        # Cache buttons for this tree
        self.cached_rune_buttons[f'secondary_{tree_name}'] = tree_buttons

    def setup_ui(self):
        """Setup the complete UI layout with modern design"""
        # Main container with clean design
        main_frame = tk.Frame(self.root, bg=UIConstants.BACKGROUND_COLOR)
        main_frame.pack(fill='both', expand=True, padx=UIConstants.MAIN_PADDING[0], 
                       pady=UIConstants.MAIN_PADDING[1])
        
        # Create main layout: Left panel | Right area
        content_frame = tk.Frame(main_frame, bg=UIConstants.BACKGROUND_COLOR)
        content_frame.pack(fill='both', expand=True)
        
        # LEFT PANEL - Champion Selection
        self.setup_champion_panel(content_frame)
        
        # RIGHT AREA - Top saved runes + Main rune area
        right_frame = tk.Frame(content_frame, bg=UIConstants.BACKGROUND_COLOR)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # TOP PANEL - Saved Rune Pages
        self.setup_saved_runes_panel(right_frame)
        
        # MAIN AREA - Rune Selection (no title)
        self.setup_rune_selection_area(right_frame)
        
        # BOTTOM - Action buttons
        self.setup_action_buttons(right_frame)
        
    def setup_champion_panel(self, parent):
        """Setup left champion selection panel"""
        champion_frame = tk.Frame(parent, bg=UIConstants.BACKGROUND_COLOR, 
                                 width=UIConstants.CHAMPION_FRAME_WIDTH)
        champion_frame.pack(side='left', fill='y', padx=(0, 5))
        champion_frame.pack_propagate(False)
        
        # Search box at top (no label)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_champions)
        search_entry = tk.Entry(champion_frame, textvariable=self.search_var, 
                               font=('Arial', UIConstants.FONT_SIZE_DEFAULT))
        search_entry.pack(fill='x')
        
        # Scrollable champion list
        canvas = tk.Canvas(champion_frame, bg=UIConstants.BACKGROUND_COLOR, 
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
        
        scrollbar = ttk.Scrollbar(champion_frame, orient="vertical", command=canvas.yview)
        self.champion_list_frame = tk.Frame(canvas, bg=UIConstants.BACKGROUND_COLOR)
        
        self.champion_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.champion_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.champion_canvas = canvas
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        self.load_champion_list()
        
    def setup_saved_runes_panel(self, parent):
        """Setup top saved runes panel with clean design"""
        saved_container = tk.Frame(parent, bg=UIConstants.BACKGROUND_COLOR)
        saved_container.pack(fill='x', pady=UIConstants.SAVED_RUNES_PADDING)
        
        # Scrollable horizontal list for saved runes
        canvas = tk.Canvas(saved_container, bg=UIConstants.BACKGROUND_COLOR, 
                          height=UIConstants.SAVED_RUNES_CANVAS_HEIGHT, highlightthickness=0)
        # Style horizontal scrollbar to match champion scrollbar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("SavedRunes.Horizontal.TScrollbar", 
                       background=UIConstants.SCROLLBAR_BG, 
                       troughcolor=UIConstants.SCROLLBAR_BG,
                       bordercolor=UIConstants.SCROLLBAR_BORDER, 
                       arrowcolor=UIConstants.SCROLLBAR_ARROW, 
                       darkcolor=UIConstants.SCROLLBAR_BORDER,
                       lightcolor=UIConstants.SCROLLBAR_BG)
        
        scrollbar_h = ttk.Scrollbar(saved_container, orient="horizontal", command=canvas.xview,
                                   style="SavedRunes.Horizontal.TScrollbar")
        self.saved_runes_frame = tk.Frame(canvas, bg=UIConstants.BACKGROUND_COLOR)
        
        self.saved_runes_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.saved_runes_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar_h.set)
        
        canvas.pack(fill="x", expand=True)
        scrollbar_h.pack(fill="x")
        
        self.saved_canvas = canvas
        
    def setup_rune_selection_area(self, parent):
        """Setup main rune selection area (without title)"""
        rune_frame = tk.Frame(parent, bg='white')
        rune_frame.pack(fill='both', expand=True)
        
        # Main content container with minimalistic design
        content_frame = tk.Frame(rune_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=8, pady=4)
        
        # Centered two-column layout with equal spacing
        columns_frame = tk.Frame(content_frame, bg='white')
        columns_frame.pack(fill='both', expand=True)
        
        # Left column - Primary (centered)
        primary_column = tk.Frame(columns_frame, bg='white')
        primary_column.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        # Primary section with clean header
        primary_header = tk.Frame(primary_column, bg='white')
        primary_header.pack(fill='x', pady=(0, 8))
        
        primary_label = tk.Label(primary_header, text="PRIMARY", 
                                font=('Arial', 11, 'bold'), fg='#2c3e50',
                                bg='white')
        primary_label.pack()
        
        # Primary tree selection
        self.primary_tree_frame = tk.Frame(primary_column, bg='white')
        self.primary_tree_frame.pack(fill='x', pady=(0, 12))
        
        # Primary runes container
        self.primary_runes_frame = tk.Frame(primary_column, bg='white')
        self.primary_runes_frame.pack(fill='both', expand=True)
        
        # Right column - Secondary (centered)
        secondary_column = tk.Frame(columns_frame, bg='white')
        secondary_column.pack(side='right', fill='both', expand=True, padx=(8, 0))
        
        # Secondary section with clean header
        secondary_header = tk.Frame(secondary_column, bg='white')
        secondary_header.pack(fill='x', pady=(0, 8))
        
        secondary_label = tk.Label(secondary_header, text="SECONDARY", 
                                  font=('Arial', 11, 'bold'), fg='#2c3e50',
                                  bg='white')
        secondary_label.pack()
        
        # Secondary tree selection
        self.secondary_tree_frame = tk.Frame(secondary_column, bg='white')
        self.secondary_tree_frame.pack(pady=(0, 12))
        
        # Secondary runes container
        self.secondary_runes_frame = tk.Frame(secondary_column, bg='white')
        self.secondary_runes_frame.pack(fill='x', pady=(0, 12))
        
        # Stat shards section
        shards_header = tk.Frame(secondary_column, bg='white')
        shards_header.pack(fill='x', pady=(0, 8))
        
        stats_label = tk.Label(shards_header, text="SHARDS", 
                              font=('Arial', 11, 'bold'), fg='#2c3e50',
                              bg='white')
        stats_label.pack()
        
        # Shards container
        self.stats_frame = tk.Frame(secondary_column, bg='white')
        self.stats_frame.pack(fill='x')
        
        # Initialize components
        self.create_tree_buttons()
        self.update_secondary_tree_options()
        self.create_stat_shards()
        
    def setup_action_buttons(self, parent):
        """Setup bottom save panel and action buttons"""
        # Clean save container
        save_container = tk.Frame(parent, bg='white', relief='solid', bd=1)
        save_container.pack(fill='x', pady=(10, 8))
        
        # Input fields with clean layout
        inputs_frame = tk.Frame(save_container, bg='white')
        inputs_frame.pack(fill='x', padx=12, pady=8)
        
        # Rune page name with buttons on same row
        name_frame = tk.Frame(inputs_frame, bg='white')
        name_frame.pack(fill='x', pady=(0, 6))
        tk.Label(name_frame, text="Rune Page Name:", font=('Arial', 11), 
                fg='#2c3e50', bg='white', width=15, anchor='w').pack(side='left')
        self.name_entry = tk.Entry(name_frame, font=('Arial', 11), width=32,
                                  relief='solid', bd=1)
        self.name_entry.pack(side='left', padx=(10, 10))
        
        # Buttons on same row as name entry
        clear_btn = tk.Button(name_frame, text="Clear", font=('Arial', 10),
                             command=self.clear_all_runes, bg='#e74c3c', fg='white',
                             relief='flat', padx=12, pady=4, cursor='hand2')
        clear_btn.pack(side='left', padx=(0, 5))
        
        save_btn = tk.Button(name_frame, text="Save", font=('Arial', 10),
                            command=self.save_rune_page_direct, bg='#3498db', fg='white',
                            relief='flat', padx=12, pady=4, cursor='hand2')
        save_btn.pack(side='left')
        
        # Matchup notes on separate row
        notes_frame = tk.Frame(inputs_frame, bg='white')
        notes_frame.pack(fill='x')
        tk.Label(notes_frame, text="Matchup Notes:", font=('Arial', 11), 
                fg='#2c3e50', bg='white', width=15, anchor='w').pack(side='left', anchor='n')
        self.notes_text = tk.Text(notes_frame, height=2, width=32, font=('Arial', 11),
                                 relief='solid', bd=1)
        self.notes_text.pack(side='left', padx=(10, 0))

    def load_champion_list(self):
        """Load and display champion list ordered by rune page count then alphabetically"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get champions with rune page counts
        cursor.execute('''
            SELECT c.id, c.name, c.image_path, COUNT(rp.id) as rune_count
            FROM champions c
            LEFT JOIN rune_pages rp ON c.id = rp.champion_id
            GROUP BY c.id, c.name, c.image_path
            ORDER BY rune_count DESC, c.name ASC
        ''')
        
        self.champions_data = cursor.fetchall()
        conn.close()
        
        self.display_champions()
        
    def display_champions(self, search_filter=""):
        self._clear_champion_display()
        matching_champions = self._filter_champions_by_name(search_filter)
        
        for champion_id, champion_name, image_path, saved_pages_count in matching_champions:
            champion_button = self._create_champion_button(champion_id, champion_name, image_path)
            
            if saved_pages_count > 0:
                self._add_rune_count_label(saved_pages_count)
            
            self.champion_buttons[champion_id] = champion_button
    
    def _clear_champion_display(self):
        for widget in self.champion_list_frame.winfo_children():
            widget.destroy()
        self.champion_buttons.clear()
    
    def _filter_champions_by_name(self, search_filter):
        matching_champions = []
        for champion_id, name, image_path, rune_count in self.champions_data:
            if search_filter.lower() in name.lower():
                matching_champions.append((champion_id, name, image_path, rune_count))
        return matching_champions
    
    def _create_champion_button(self, champion_id, champion_name, image_path):
        champion_image = self.load_champion_image(image_path, size=UIConstants.CHAMPION_IMAGE_SIZE)
        
        button = tk.Button(self.champion_list_frame, image=champion_image,
                          width=UIConstants.CHAMPION_BUTTON_SIZE[0], 
                          height=UIConstants.CHAMPION_BUTTON_SIZE[1], 
                          relief='raised', bd=UIConstants.BORDER_WIDTH,
                          command=lambda: self.select_champion(champion_id, champion_name))
        button.image = champion_image
        button.pack(pady=UIConstants.CHAMPION_BUTTON_PADDING)
        return button
    
    def _add_rune_count_label(self, rune_count):
        count_label = tk.Label(self.champion_list_frame, text=f"({rune_count})",
                              font=('Arial', UIConstants.FONT_SIZE_DEFAULT), 
                              bg=UIConstants.BACKGROUND_COLOR)
        count_label.pack()
            
    def filter_champions(self, *args):
        search_text = self.search_var.get()
        self.display_champions(search_text)
        
    def select_champion(self, champion_id, champion_name):
        """Select a champion and load their rune pages"""
        self.selected_champion = {'id': champion_id, 'name': champion_name}
        
        # Update visual feedback - only update if needed to avoid flicker
        if hasattr(self, 'last_selected_champion') and self.last_selected_champion:
            # Reset previously selected champion
            if self.last_selected_champion in self.champion_buttons:
                self.champion_buttons[self.last_selected_champion].configure(
                    relief='raised', bg=UIConstants.BUTTON_SYSTEM_BG)
        
        # Highlight new selection
        if champion_id in self.champion_buttons:
            self.champion_buttons[champion_id].configure(
                relief='sunken', bg=UIConstants.CHAMPION_SELECTED_BG)
        
        self.last_selected_champion = champion_id
        
        # Load champion's rune pages
        self.load_champion_rune_pages()
        
        # Auto-load default rune page if exists
        self.load_default_rune_page()
    
    def _load_rune_page_data(self, result):
        """Helper method to load rune page data from database result"""
        if not result:
            return
            
        primary_tree, secondary_tree, keystone, primary_runes, secondary_runes, stat_shards = result
        
        # Load the rune configuration
        self.selected_primary_tree = primary_tree
        self.selected_secondary_tree = secondary_tree
        self.selected_runes['keystone'] = keystone
        
        if primary_runes:
            primary_data = json.loads(primary_runes)
            for key, value in primary_data.items():
                self.selected_runes[key] = value
                
        if secondary_runes:
            secondary_data = json.loads(secondary_runes)
            for key, value in secondary_data.items():
                self.selected_runes[key] = value
                
        if stat_shards:
            shard_data = json.loads(stat_shards)
            self.selected_runes['stat_shards'] = shard_data
        
        # Rebuild secondary rune selection order based on loaded data
        self.secondary_rune_selection_order = []
        for row_type in ['secondary_row1', 'secondary_row2', 'secondary_row3']:
            if self.selected_runes[row_type]:
                self.secondary_rune_selection_order.append((row_type, self.selected_runes[row_type]))
            
        # Update UI
        self.update_tree_selection_visual()
        self.display_primary_runes()
        self.update_secondary_tree_options()
        self.display_secondary_runes()
        self.update_all_rune_visuals()
    
    def _create_rune_button(self, parent, item_name, image, button_config, command):
        """Helper method to create rune buttons with consistent styling"""
        btn = tk.Button(parent, image=image,
                       width=button_config.get('width', 100), 
                       height=button_config.get('height', 60), 
                       bg=UIConstants.BUTTON_DEFAULT_BG, fg=UIConstants.BUTTON_DEFAULT_FG, 
                       relief='raised', command=command)
        btn.image = image  # Keep reference
        return btn
    
    def _update_button_visuals(self, button_dict, selected_items, category_filter=None):
        """Helper method to update button visuals with reset-then-highlight pattern"""
        # Reset all buttons to default state
        for key, btn in button_dict.items():
            if category_filter is None or key[0] in category_filter:
                btn.configure(bg=UIConstants.BUTTON_DEFAULT_BG, 
                             fg=UIConstants.BUTTON_DEFAULT_FG, relief='raised')
        
        # Highlight selected items
        for key, btn in button_dict.items():
            if category_filter is None or key[0] in category_filter:
                if key in selected_items:
                    btn.configure(bg=UIConstants.BUTTON_SELECTED_BG, 
                                 fg=UIConstants.BUTTON_SELECTED_FG, relief='sunken')
    
    def _execute_db_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Helper method for database operations with consistent connection handling"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None
                
            conn.commit()
            return result
        finally:
            conn.close()
        
    def load_champion_rune_pages(self):
        """Load and display saved rune pages for selected champion"""
        if not self.selected_champion:
            return
            
        # Clear existing saved rune displays
        for widget in self.saved_runes_frame.winfo_children():
            widget.destroy()
            
        # Get rune pages for this champion, sorted by default first, then primary/secondary tree
        rune_pages = self._execute_db_query('''
            SELECT id, name, primary_tree, secondary_tree, keystone, notes, is_default
            FROM rune_pages 
            WHERE champion_id = ?
            ORDER BY is_default DESC, primary_tree, secondary_tree
        ''', (self.selected_champion['id'],), fetch_all=True)
        
        # Display each rune page
        for i, (page_id, name, primary_tree, secondary_tree, keystone, notes, is_default) in enumerate(rune_pages):
            self.create_rune_page_box(page_id, name, primary_tree, secondary_tree, keystone, notes, bool(is_default))
            
        # Update canvas scroll region (defer to reduce UI lag)
        self.root.after_idle(lambda: [
            self.saved_runes_frame.update_idletasks(),
            self.saved_canvas.configure(scrollregion=self.saved_canvas.bbox("all"))
        ])
        
    def create_rune_page_box(self, page_id, name, primary_tree, secondary_tree, keystone, notes, is_default):
        """Create a visual box for a saved rune page"""
        box_frame = tk.Frame(self.saved_runes_frame, relief='raised', 
                            bd=UIConstants.BORDER_WIDTH, 
                            bg=UIConstants.DEFAULT_RUNE_PAGE_BG if is_default else UIConstants.BACKGROUND_COLOR)
        box_frame.pack(side='left', padx=UIConstants.RUNE_PAGE_BOX_PADDING[0], 
                      pady=UIConstants.RUNE_PAGE_BOX_PADDING[1])
        
        # Keystone icon as button for better click handling
        icon_label = None
        if keystone:
            keystone_icon = self.load_rune_image(keystone, size=UIConstants.RUNE_PAGE_ICON_SIZE)
            icon_label = tk.Button(box_frame, image=keystone_icon, bg=box_frame['bg'],
                                  bd=0, relief='flat', activebackground=box_frame['bg'])
            icon_label.image = keystone_icon
            icon_label.pack(pady=UIConstants.ICON_PADDING)
        
        # Delete button
        delete_btn = tk.Button(box_frame, text="×", 
                              font=('Arial', UIConstants.FONT_SIZE_DELETE_BUTTON, 'bold'),
                              fg=UIConstants.DELETE_BUTTON_FG, bg=box_frame['bg'], bd=0,
                              width=UIConstants.DELETE_BUTTON_SIZE[0], 
                              height=UIConstants.DELETE_BUTTON_SIZE[1],
                              command=lambda: self.delete_rune_page(page_id))
        delete_btn.pack(pady=UIConstants.DELETE_BUTTON_PADDING)
            
        # Make all widgets clickable by binding to each one
        def on_click(event=None):
            self.load_rune_page_by_id(page_id)
        
        def on_double_click(event=None):
            self.set_as_default(page_id)
        
        # Bind click events to all widgets
        box_frame.bind("<Button-1>", on_click)
        box_frame.bind("<Double-Button-1>", on_double_click)
        
        if icon_label:
            icon_label.configure(command=lambda: on_click())
            icon_label.bind("<Double-Button-1>", on_double_click)
        
        # Make delete button NOT propagate clicks to parent
        delete_btn.bind("<Button-1>", lambda e: "break")
            
        # Tooltip for hover on all widgets including delete button
        tooltip_text = name
        if notes and notes.strip():
            tooltip_text += f"\n{notes.strip()}"
        
        all_widgets = [box_frame, delete_btn]
        if icon_label:
            all_widgets.append(icon_label)
        
        for widget in all_widgets:
            self.create_tooltip(widget, tooltip_text)
        
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            # Clean up any existing tooltip first
            cleanup_tooltip()
                
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tooltip.configure(bg='lightyellow')
            label = tk.Label(tooltip, text=text, background='lightyellow',
                           font=('Arial', 11), relief='solid', borderwidth=1,
                           justify='left')
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
        
        # Bind to multiple events to ensure reliable behavior
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", lambda e: cleanup_tooltip())
        widget.bind("<FocusOut>", lambda e: cleanup_tooltip())
        
    def load_default_rune_page(self):
        """Load the default rune page for selected champion"""
        if not self.selected_champion:
            return
            
        result = self._execute_db_query('''
            SELECT primary_tree, secondary_tree, keystone, primary_runes, 
                   secondary_runes, stat_shards
            FROM rune_pages 
            WHERE champion_id = ? AND is_default = 1
            LIMIT 1
        ''', (self.selected_champion['id'],), fetch_one=True)
        
        self._load_rune_page_data(result)
            
    def load_rune_page_by_id(self, page_id):
        """Load a specific rune page by ID"""
        result = self._execute_db_query('''
            SELECT primary_tree, secondary_tree, keystone, primary_runes, 
                   secondary_runes, stat_shards
            FROM rune_pages 
            WHERE id = ?
        ''', (page_id,), fetch_one=True)
        
        self._load_rune_page_data(result)

    def create_tree_buttons(self):
        """Create rune tree selection buttons"""
        tree_frame = tk.Frame(self.primary_tree_frame, bg='white')
        tree_frame.pack()
        
        self.tree_buttons = {}
        for i, (tree_name, tree_data) in enumerate(self.rune_trees.items()):
            # Load tree icon
            tree_icon = self.load_tree_icon(tree_name, size=UIConstants.TREE_ICON_SIZE)
            
            btn = tk.Button(tree_frame, image=tree_icon, text=tree_name, 
                           font=('Arial', UIConstants.FONT_SIZE_TREE_BUTTON, 'bold'), compound='top',
                           bg=tree_data['color'], fg=UIConstants.BUTTON_SELECTED_FG,
                           width=UIConstants.TREE_BUTTON_SIZE[0], 
                           height=UIConstants.TREE_BUTTON_SIZE[1], 
                           wraplength=UIConstants.TREE_BUTTON_WRAP_LENGTH,
                           command=lambda t=tree_name: self.select_primary_tree(t))
            btn.image = tree_icon  # Keep a reference
            btn.grid(row=0, column=i, padx=UIConstants.TREE_BUTTON_PADDING)
            self.tree_buttons[tree_name] = btn
    
    def create_stat_shards(self):
        """Create stat shard selection interface"""
        shard_types = ['offense', 'flex', 'defense']
        colors = ['#C83E3A', '#C8AA6E', '#A1D586']
        
        for i, (shard_type, color) in enumerate(zip(shard_types, colors)):
            shard_frame = tk.Frame(self.stats_frame, bg='white')
            shard_frame.grid(row=i, column=0, pady=(0, 3))
            # Center the shard frame within its grid cell
            self.stats_frame.grid_columnconfigure(0, weight=1)
            
            for j, shard in enumerate(self.stat_shards[shard_type]):
                shard_image = self.load_stat_shard_image(shard, size=(20, 20))
                config = {'width': 25, 'height': 25}
                btn = self._create_rune_button(shard_frame, shard, shard_image, config,
                                             lambda st=shard_type, s=shard: self.select_stat_shard(st, s))
                btn.grid(row=0, column=j, padx=1)
                self.stat_buttons[(shard_type, shard)] = btn

    def select_primary_tree(self, tree_name):
        """Select primary rune tree"""
        # Don't do anything if tree is already selected (prevents flickering)
        if self.selected_primary_tree == tree_name:
            return
            
        # If this tree is currently selected as secondary, reset secondary selection
        if self.selected_secondary_tree == tree_name:
            self.selected_secondary_tree = None
            # Clear secondary rune selections
            for key in ['secondary_row1', 'secondary_row2', 'secondary_row3']:
                self.selected_runes[key] = None
            # Clear secondary rune selection order
            self.secondary_rune_selection_order = []
            
        self.selected_primary_tree = tree_name
        
        self.update_tree_selection_visual()
        self.display_primary_runes()
        self.update_secondary_tree_options()
        
    def update_tree_selection_visual(self):
        """Update visual feedback for tree selection"""
        # Update button appearance while preserving tree colors
        for name, btn in self.tree_buttons.items():
            tree_color = self.rune_trees[name]['color']
            if name == self.selected_primary_tree:
                btn.configure(relief='sunken', bg=tree_color, bd=2)
            else:
                btn.configure(relief='raised', bg=tree_color, bd=2)

    def display_primary_runes(self):
        """Display runes for selected primary tree using cached widgets"""
        # Hide all primary tree widgets
        for widget in self.primary_tree_widgets.values():
            widget.pack_forget()
        
        # Clear old button references
        self.rune_buttons = {k: v for k, v in self.rune_buttons.items() 
                            if not k[0].startswith(('keystone', 'primary_'))}
        
        if not self.selected_primary_tree:
            return
        
        # Show the cached widget for selected tree
        widget = self.primary_tree_widgets[self.selected_primary_tree]
        widget.pack(fill='both', expand=True)
        
        # Restore button references for this tree
        tree_buttons = self.cached_rune_buttons[f'primary_{self.selected_primary_tree}']
        self.rune_buttons.update(tree_buttons)

    def update_secondary_tree_options(self):
        """Update secondary tree selection options"""
        # Clear existing secondary tree buttons
        for widget in self.secondary_tree_frame.winfo_children():
            widget.destroy()
        
        # Show all trees, but disable the primary tree
        all_trees = list(self.rune_trees.keys())
        
        for i, tree_name in enumerate(all_trees):
            tree_data = self.rune_trees[tree_name]
            is_primary = (tree_name == self.selected_primary_tree)
            
            btn = tk.Button(self.secondary_tree_frame, text=tree_name,
                           font=('Arial', 9, 'bold'), wraplength=70,
                           width=10, height=2,
                           command=lambda t=tree_name: self.select_secondary_tree(t))
            
            if is_primary:
                # Disable primary tree - gray it out
                btn.configure(bg='#2C2C2C', fg='#666666', state='disabled')
            else:
                # Normal selectable tree
                btn.configure(bg=tree_data['color'], fg='black', state='normal')
            
            btn.grid(row=0, column=i, padx=2, pady=2)
    
    def select_secondary_tree(self, tree_name):
        """Select secondary rune tree"""
        # Don't do anything if tree is already selected (prevents flickering)
        if self.selected_secondary_tree == tree_name:
            return
        
        # Clear previous secondary selections when changing trees
        for key in ['secondary_row1', 'secondary_row2', 'secondary_row3']:
            self.selected_runes[key] = None
        # Clear secondary rune selection order
        self.secondary_rune_selection_order = []
            
        self.selected_secondary_tree = tree_name
        self.display_secondary_runes()
    
    def display_secondary_runes(self):
        """Display secondary tree runes using cached widgets"""
        # Hide all secondary tree widgets
        for widget in self.secondary_tree_widgets.values():
            widget.pack_forget()
        
        # Clear old button references
        self.rune_buttons = {k: v for k, v in self.rune_buttons.items() 
                            if not k[0].startswith('secondary_')}
        
        if not self.selected_secondary_tree:
            return
        
        # Show the cached widget for selected tree
        widget = self.secondary_tree_widgets[self.selected_secondary_tree]
        widget.pack(fill='x', pady=(0, 12))
        
        # Restore button references for this tree
        tree_buttons = self.cached_rune_buttons[f'secondary_{self.selected_secondary_tree}']
        self.rune_buttons.update(tree_buttons)

    def select_rune(self, rune_type, rune_name):
        """Select a specific rune"""
        # Special logic for secondary runes (FIFO with max 2 selections)
        if rune_type.startswith('secondary_'):
            self._handle_secondary_rune_selection(rune_type, rune_name)
        else:
            # Normal selection for primary runes and keystones
            self.selected_runes[rune_type] = rune_name
            # Update visual feedback - highlight selected rune
            self.update_rune_selection_visual(rune_type, rune_name)
    
    def _handle_secondary_rune_selection(self, row_type, rune_name):
        if self._is_rune_already_selected(row_type, rune_name):
            return
        
        if self._is_replacing_same_row_rune(row_type):
            self._remove_old_rune_from_tracking(row_type)
        elif self._should_remove_oldest_rune(row_type):
            self._remove_oldest_selected_rune()
        
        self._select_new_secondary_rune(row_type, rune_name)
        self.update_all_secondary_rune_visuals()
    
    def _is_rune_already_selected(self, row_type, rune_name):
        return self.selected_runes[row_type] == rune_name
    
    def _is_replacing_same_row_rune(self, row_type):
        return self.selected_runes[row_type] is not None
    
    def _remove_old_rune_from_tracking(self, row_type):
        old_rune = self.selected_runes[row_type]
        old_selection = (row_type, old_rune)
        if old_selection in self.secondary_rune_selection_order:
            self.secondary_rune_selection_order.remove(old_selection)
    
    def _should_remove_oldest_rune(self, row_type):
        current_selections = self._get_current_secondary_selections()
        selected_rows = [row for row, _ in current_selections]
        return len(current_selections) >= 2 and row_type not in selected_rows
    
    def _get_current_secondary_selections(self):
        selections = []
        for row_type in ['secondary_row1', 'secondary_row2', 'secondary_row3']:
            if self.selected_runes[row_type]:
                selections.append((row_type, self.selected_runes[row_type]))
        return selections
    
    def _remove_oldest_selected_rune(self):
        if self.secondary_rune_selection_order:
            oldest_row_type, oldest_rune = self.secondary_rune_selection_order.pop(0)
            self.selected_runes[oldest_row_type] = None
    
    def _select_new_secondary_rune(self, row_type, rune_name):
        self.selected_runes[row_type] = rune_name
        new_selection = (row_type, rune_name)
        if new_selection not in self.secondary_rune_selection_order:
            self.secondary_rune_selection_order.append(new_selection)
    
    def update_all_secondary_rune_visuals(self):
        """Update visual feedback for all secondary runes"""
        secondary_filter = ['secondary_row1', 'secondary_row2', 'secondary_row3']
        selected_items = {(row_type, self.selected_runes[row_type]) for row_type in secondary_filter 
                         if self.selected_runes[row_type]}
        self._update_button_visuals(self.rune_buttons, selected_items, secondary_filter)
    
    def update_rune_selection_visual(self, rune_type, selected_rune):
        """Update visual feedback for rune selection"""
        selected_items = {(rune_type, selected_rune)}
        self._update_button_visuals(self.rune_buttons, selected_items, [rune_type])

    def select_stat_shard(self, shard_type, shard_name):
        """Select a stat shard"""
        self.selected_runes['stat_shards'][shard_type] = shard_name
        
        # Update visual feedback for stat shards
        selected_items = {(shard_type, shard_name)}
        self._update_button_visuals(self.stat_buttons, selected_items, [shard_type])
        
        # Shard selected
        
    def update_all_rune_visuals(self):
        """Update visual feedback for all selected runes"""
        # Update primary tree visual
        if self.selected_primary_tree:
            self.update_tree_selection_visual()
        
        # Collect all selected runes
        selected_runes = {(rune_type, rune_name) for rune_type, rune_name in self.selected_runes.items() 
                         if rune_name and rune_type != 'stat_shards'}
        self._update_button_visuals(self.rune_buttons, selected_runes)
        
        # Collect all selected stat shards
        selected_shards = {(shard_type, shard_name) for shard_type, shard_name in self.selected_runes['stat_shards'].items() 
                          if shard_name}
        self._update_button_visuals(self.stat_buttons, selected_shards)

    def clear_all_runes(self):
        """Clear all selected runes"""
        self.selected_primary_tree = None
        self.selected_secondary_tree = None
        self.selected_runes = {
            'keystone': None,
            'primary_row1': None,
            'primary_row2': None,
            'primary_row3': None,
            'secondary_row1': None,
            'secondary_row2': None,
            'stat_shards': {'offense': None, 'flex': None, 'defense': None}
        }
        # Clear secondary rune selection order
        self.secondary_rune_selection_order = []
        
        # Clear UI
        for widget in self.primary_runes_frame.winfo_children():
            widget.destroy()
        for widget in self.secondary_runes_frame.winfo_children():
            widget.destroy()
        
        # Reset tree button styles
        for btn in self.tree_buttons.values():
            btn.configure(relief='raised', bd=1)
        
        # Reset all rune and stat button styles (only if they still exist)
        try:
            for btn in self.rune_buttons.values():
                btn.configure(bg='#3C3C41', fg='white', relief='raised')
        except:
            pass  # Buttons may have been destroyed
        
        try:
            for btn in self.stat_buttons.values():
                btn.configure(bg='#3C3C41', fg='white', relief='raised')
        except:
            pass  # Buttons may have been destroyed
        
        # Clear button dictionaries
        self.rune_buttons.clear()

    def save_rune_page_direct(self):
        """Save the current rune configuration using integrated UI fields"""
        if not self.selected_primary_tree:
            messagebox.showwarning("Incomplete Build", 
                                 "Please select a primary tree first!")
            return
            
        if not self.selected_runes['keystone']:
            messagebox.showwarning("Incomplete Build", 
                                 "Please select a keystone rune!")
            return
            
        if not self.selected_champion:
            messagebox.showwarning("Missing Champion", 
                                 "Please select a champion first!")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a rune page name!")
            return
            
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        # Prepare rune data
        primary_runes = {
            'primary_row1': self.selected_runes['primary_row1'],
            'primary_row2': self.selected_runes['primary_row2'],
            'primary_row3': self.selected_runes['primary_row3']
        }
        
        secondary_runes = {
            'secondary_row1': self.selected_runes['secondary_row1'],
            'secondary_row2': self.selected_runes['secondary_row2'],
            'secondary_row3': self.selected_runes['secondary_row3']
        }
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rune_pages 
            (name, champion_id, primary_tree, secondary_tree, keystone, 
             primary_runes, secondary_runes, stat_shards, notes, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, self.selected_champion['id'], self.selected_primary_tree, self.selected_secondary_tree,
            self.selected_runes['keystone'], json.dumps(primary_runes),
            json.dumps(secondary_runes), json.dumps(self.selected_runes['stat_shards']),
            notes, False
        ))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"Rune page '{name}' saved successfully!")
        
        # Clear the input fields
        self.name_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        
        # Refresh the champion's rune pages
        self.load_champion_rune_pages()
    
    def set_as_default(self, page_id):
        """Set a rune page as the default for the current champion"""
        if not self.selected_champion:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Remove default from all other pages for this champion
        cursor.execute(
            "UPDATE rune_pages SET is_default = 0 WHERE champion_id = ?",
            (self.selected_champion['id'],)
        )
        
        # Set this page as default
        cursor.execute(
            "UPDATE rune_pages SET is_default = 1 WHERE id = ?",
            (page_id,)
        )
        
        conn.commit()
        conn.close()
        
        # Refresh the display
        self.load_champion_rune_pages()

    def delete_rune_page(self, page_id):
        """Delete a rune page after confirmation"""
        result = messagebox.askyesno("Delete Rune Page", 
                                   "Are you sure you want to delete this rune page?")
        if result:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM rune_pages WHERE id = ?", (page_id,))
            
            conn.commit()
            conn.close()
            
            # Refresh the display
            self.load_champion_rune_pages()

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ChampionRuneBuilder()
    app.run()