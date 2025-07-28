import os
from PIL import Image, ImageTk, ImageDraw
from typing import List, Tuple, Dict, Optional
from views.ui_constants import UIConstants


class ImageLoader:
    """Handles image loading, caching, and placeholder generation"""
    
    def __init__(self):
        self.image_cache: Dict[str, ImageTk.PhotoImage] = {}
        
    def load_image_with_fallback(self, path_patterns: List[str], size: Tuple[int, int], 
                               cache_prefix: str, placeholder_text: str = "", 
                               placeholder_color: str = UIConstants.PLACEHOLDER_COLOR) -> ImageTk.PhotoImage:
        """Unified image loading with fallback and caching"""
        cache_key = f"{cache_prefix}_{hash(str(path_patterns))}_{size}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
            
        # Try to load from each possible path
        for path in path_patterns:
            try:
                if os.path.exists(path):
                    # Use faster NEAREST for smaller images to speed up loading
                    resample = Image.Resampling.NEAREST if size[0] <= 50 else Image.Resampling.LANCZOS
                    img = Image.open(path).resize(size, resample)
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[cache_key] = photo
                    return photo
            except Exception:
                continue
        
        # Create placeholder if no image found
        photo = self.create_placeholder_image(size, color=placeholder_color, text=placeholder_text)
        self.image_cache[cache_key] = photo
        return photo
        
    def load_champion_image(self, image_path: str, size: Tuple[int, int] = UIConstants.CHAMPION_IMAGE_SIZE) -> ImageTk.PhotoImage:
        """Load champion image with fallback and caching"""
        return self.load_image_with_fallback([image_path], size, "champion", "?")
        
    def load_rune_image(self, rune_name: str, size: Tuple[int, int] = (64, 64)) -> ImageTk.PhotoImage:
        """Load a rune image from the file system or create placeholder with caching"""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rune_name_clean = rune_name.replace(" ", "_").replace("'", "").replace(":", "-")
        
        possible_paths = [
            os.path.join(script_dir, 'data', 'rune_icons', f'52px-{rune_name_clean}_rune.png'),
            os.path.join(script_dir, 'data', 'rune_icons', f'52px-{rune_name.replace(" ", "_")}_rune.png'),
            os.path.join(script_dir, 'data', 'rune_icons', f'{rune_name_clean}.png'),
            os.path.join(script_dir, 'data', 'rune_icons', f'{rune_name}.png'),
        ]
        
        return self.load_image_with_fallback(possible_paths, size, "rune", rune_name[:UIConstants.RUNE_PLACEHOLDER_TEXT_LENGTH])
    
    def load_tree_icon(self, tree_name: str, tree_color: str, size: Tuple[int, int] = UIConstants.TREE_ICON_DISPLAY_SIZE) -> ImageTk.PhotoImage:
        """Load a tree icon or create placeholder"""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        possible_paths = [
            os.path.join(script_dir, 'data', 'rune_icons', f'52px-{tree_name}_icon.png'),
            os.path.join(script_dir, 'data', 'rune_icons', f'{tree_name}_icon.png'),
            os.path.join(script_dir, 'data', 'rune_icons', f'52px-{tree_name}_icon.png'),
            os.path.join(script_dir, 'data', 'rune_icons', f'{tree_name}_icon.png'),
        ]
        
        return self.load_image_with_fallback(possible_paths, size, "tree", tree_name[:4], tree_color)
    
    def load_stat_shard_image(self, shard_name: str, size: Tuple[int, int] = UIConstants.STAT_SHARD_IMAGE_SIZE) -> ImageTk.PhotoImage:
        """Load a stat shard image or create placeholder with caching"""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        shard_mapping = {
            'Adaptive Force': 'Adaptive_Force', 'Attack Speed': 'Attack_Speed', 'Ability Haste': 'Ability_Haste',
            'Armor': 'Armor', 'Magic Resist': 'Magic_Resist', 'Health': 'Health',
            'Movement Speed': 'Movement_Speed', 'Health Scaling': 'Health_Scaling',
            'Tenacity and Slow Resist': 'Tenacity_and_Slow_Resist'
        }
        
        file_name = shard_mapping.get(shard_name, shard_name.replace(' ', '_'))
        possible_paths = [
            os.path.join(script_dir, 'data', 'shard_icons', f'30px-Rune_shard_{file_name}.png'),
            os.path.join(script_dir, 'data', 'shard_icons', f'{file_name}.png'),
            os.path.join(script_dir, 'data', 'shard_icons', f'Rune_shard_{file_name}.png'),
        ]
        
        color = self._get_stat_shard_color(shard_name)
        return self.load_image_with_fallback(possible_paths, size, "shard", shard_name[:3], color)
    
    def _get_stat_shard_color(self, shard_name: str) -> str:
        """Get color for stat shard based on type"""
        shard_colors = {
            'offense': '#C83E3A',
            'flex': '#C8AA6E', 
            'defense': '#A1D586'
        }
        
        offense_keywords = ['Force', 'Speed', 'Haste']
        flex_keywords = ['Armor', 'Resist']
        
        if any(keyword in shard_name for keyword in offense_keywords):
            return shard_colors['offense']
        elif any(keyword in shard_name for keyword in flex_keywords):
            return shard_colors['flex']
        else:
            return shard_colors['defense']
        
    def create_placeholder_image(self, size: Tuple[int, int], color: str = UIConstants.PLACEHOLDER_COLOR, text: str = '') -> ImageTk.PhotoImage:
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