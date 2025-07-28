class UIConstants:
    """UI constants and styling configuration"""
    
    # Main window
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 750
    
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
    
    # Stat shards - using original 30px resolution
    STAT_SHARD_IMAGE_SIZE = (30, 30)
    STAT_SHARD_BUTTON_SIZE = (110, 70)
    STAT_SHARD_PADDING = 1
    STAT_SHARD_WRAP_LENGTH = 105
    
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
    
    # Color Palette
    # Cadet Grey – #959BB5
    # Chinese Black – #0A1123
    # American Blue – #3A3E6C
    # Ube – #8387C3
    # Cool Grey – #8A8CAC
    
    # Color scheme
    BACKGROUND_COLOR = '#0A1123'  # Chinese Black
    TEXT_COLOR = '#959BB5'        # Cadet Grey
    PLACEHOLDER_COLOR = '#3A3E6C' # American Blue
    
    # Button colors
    BUTTON_DEFAULT_BG = '#3A3E6C'  # American Blue
    BUTTON_DEFAULT_FG = '#959BB5'  # Cadet Grey
    BUTTON_SELECTED_BG = '#8387C3' # Ube
    BUTTON_SELECTED_FG = '#0A1123' # Chinese Black
    BUTTON_OPTIONAL_BG = '#6A5ACD' # Slate Blue (for optional runes)
    BUTTON_OPTIONAL_FG = '#F0F8FF' # Alice Blue (for optional runes text)
    BUTTON_SYSTEM_BG = '#8A8CAC'   # Cool Grey
    DELETE_BUTTON_FG = '#8387C3'   # Ube (for delete button)
    
    # Special highlights
    DEFAULT_RUNE_PAGE_BG = '#8387C3'  # Ube
    CHAMPION_SELECTED_BG = '#8A8CAC'  # Cool Grey
    TOOLTIP_BG = '#8A8CAC'           # Cool Grey
    
    # Scrollbar styling
    SCROLLBAR_BG = '#3A3E6C'      # American Blue
    SCROLLBAR_BORDER = '#8A8CAC'  # Cool Grey
    SCROLLBAR_ARROW = '#959BB5'   # Cadet Grey
    
    # Database performance
    DB_CACHE_SIZE = 10000
    DB_MMAP_SIZE = 268435456  # 256MB