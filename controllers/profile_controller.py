from typing import List, Tuple, Optional, Set, Callable
from models.profile_model import ProfileModel
from views.profile_dialog import ProfileDialog
from views.image_loader import ImageLoader


class ProfileController:
    """Controller for managing champion profiles"""
    
    def __init__(self, profile_model: ProfileModel, image_loader: ImageLoader):
        self.profile_model = profile_model
        self.image_loader = image_loader
        self.champions_data: List[Tuple] = []
        
        # Callbacks
        self.on_profile_created: Optional[Callable] = None
        self.on_profile_updated: Optional[Callable] = None
        self.on_profile_deleted: Optional[Callable] = None
        
    def set_champions_data(self, champions_data: List[Tuple]):
        """Set the champions data for the profile dialogs"""
        self.champions_data = champions_data
        
    def show_create_profile_dialog(self, parent) -> Optional[int]:
        """Show dialog to create a new profile"""
        dialog = ProfileDialog(parent, self.image_loader, self.champions_data)
        result = dialog.show()
        
        if result and result[0] == 'save':
            _, name, champion_ids = result
            profile_id = self.profile_model.save_profile(name, champion_ids)
            if self.on_profile_created:
                self.on_profile_created(profile_id)
            return profile_id
        return None
        
    def show_edit_profile_dialog(self, parent, profile_id: int) -> bool:
        """Show dialog to edit an existing profile"""
        # Get existing profile data
        profile_info = self.profile_model.get_profile_by_id(profile_id)
        if not profile_info:
            return False
            
        # Get existing champion selections
        champion_ids = self.profile_model.get_profile_champion_ids(profile_id)
        selected_champion_ids = set(champion_ids)
        
        dialog = ProfileDialog(parent, self.image_loader, self.champions_data, 
                             profile_info, selected_champion_ids)
        result = dialog.show()
        
        if result:
            if result[0] == 'save':
                _, name, new_champion_ids = result
                self.profile_model.update_profile(profile_id, name, new_champion_ids)
                if self.on_profile_updated:
                    self.on_profile_updated(profile_id)
                return True
            elif result[0] == 'delete':
                _, delete_profile_id = result
                self.delete_profile(delete_profile_id)
                return True
        return False
        
    def get_all_profiles(self) -> List[Tuple[int, str]]:
        """Get all profiles"""
        return self.profile_model.get_all_profiles()
        
    def get_profile_champions(self, profile_id: int) -> List[Tuple[int, str]]:
        """Get champions in a profile"""
        return self.profile_model.get_profile_champions(profile_id)
        
    def get_profile_champion_ids(self, profile_id: int) -> List[int]:
        """Get champion IDs for a profile"""
        return self.profile_model.get_profile_champion_ids(profile_id)
        
    def delete_profile(self, profile_id: int):
        """Delete a profile"""
        self.profile_model.delete_profile(profile_id)
        if self.on_profile_deleted:
            self.on_profile_deleted(profile_id)
            
    def set_callbacks(self, on_created: Callable = None, on_updated: Callable = None, 
                     on_deleted: Callable = None):
        """Set callbacks for profile events"""
        self.on_profile_created = on_created
        self.on_profile_updated = on_updated
        self.on_profile_deleted = on_deleted