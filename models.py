"""
models.py - Data Models and Session Management
Handles photo data, session state, and Excel operations
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import shutil
import os


class PhotoSession:
    """Manages the current photo session"""
    
    def __init__(self, config):
        self.config = config
        self.photos = []
        self.project_folder = None
        self.trash_folder = config.trash_dir
        self.deleted_photos = []  # For undo functionality (limited by config)
        self.pending_saves = 0  # For batch saving
    
    def set_project_folder(self, folder):
        """Set the project folder for this session"""
        self.project_folder = Path(folder)
    
    def load_from_excel(self):
        """Load existing session data from Excel"""
        if not self.config.session_file.exists():
            self._init_excel()
            return
        
        try:
            df = pd.read_excel(self.config.session_file, engine='openpyxl')
            self.photos = []
            
            for _, row in df.iterrows():
                self.photos.append({
                    'timestamp': row['Timestamp'],
                    'subfolder': row['Subfolder'],
                    'name': row['Name'],
                    'filename': row['Filename'],
                    'file_path': row['File Path']
                })
        except Exception as e:
            print(f"Error loading session: {e}")
            self._init_excel()
    
    def _init_excel(self):
        """Initialize empty Excel file"""
        df = pd.DataFrame(columns=["Timestamp", "Subfolder", "Name", "Filename", "File Path"])
        try:
            df.to_excel(self.config.session_file, index=False, engine='openpyxl')
            return True
        except Exception as e:
            print(f"Error initializing Excel: {e}")
            return False
    
    def add_photo(self, subfolder, name, captured_frame):
        """
        Add a photo to the session
        Returns: dict with status and data
        """
        timestamp = datetime.now()
        
        # Create subfolder
        subfolder_path = self.project_folder / subfolder
        try:
            subfolder_path.mkdir(exist_ok=True)
        except Exception as e:
            return {'status': 'error', 'message': f'Cannot create subfolder: {e}'}
        
        # Generate filename
        filename = f"{name}.jpg"
        file_path = subfolder_path / filename
        
        # Check for duplicates BEFORE saving
        if file_path.exists():
            duplicate_result = self._handle_duplicate_check(file_path, name, subfolder_path)
            
            if duplicate_result['status'] == 'ask':
                # Need user input - return to UI for decision
                return {
                    'status': 'duplicate',
                    'name': name,
                    'subfolder': subfolder,
                    'existing_path': str(file_path),
                    'frame': captured_frame
                }
            elif duplicate_result['status'] == 'new_path':
                file_path = duplicate_result['path']
                filename = file_path.name
            elif duplicate_result['status'] == 'replace':
                # Move old file to trash
                self._move_to_trash(file_path)
        
        # Save photo to disk
        try:
            import cv2
            cv2.imwrite(str(file_path), captured_frame)
        except Exception as e:
            return {'status': 'error', 'message': f'Cannot save photo: {e}'}
        
        # Create photo data
        photo_data = {
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'subfolder': subfolder,
            'name': name,
            'filename': filename,
            'file_path': str(file_path)
        }
        
        # Add to session
        self.photos.append(photo_data)
        
        # Save to Excel (with error handling)
        save_result = self._append_to_excel(photo_data)
        
        # Save active session for crash recovery
        self._save_active_session()
        
        return {
            'status': 'success',
            'data': photo_data,
            'save_error': save_result.get('error') if isinstance(save_result, dict) else None
        }
    
    def _handle_duplicate_check(self, path, name, folder):
        """
        Check duplicate handling based on user settings
        Returns: dict with status and action
        """
        handling = self.config.get_setting("duplicate_handling", "ask")
        
        if handling == "auto_increment":
            # Find next available number
            counter = 2
            while path.exists():
                new_name = f"{name}_{counter}.jpg"
                path = folder / new_name
                counter += 1
            return {'status': 'new_path', 'path': path}
        
        elif handling == "replace":
            return {'status': 'replace', 'path': path}
        
        else:  # ask
            return {'status': 'ask', 'path': path}
    
    def _append_to_excel(self, photo_data):
        """Append photo data to Excel file with error handling"""
        try:
            df = pd.read_excel(self.config.session_file, engine='openpyxl')
            new_row = pd.DataFrame([photo_data])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(self.config.session_file, index=False, engine='openpyxl')
            return {'status': 'success'}
            
        except PermissionError:
            error_msg = "Excel file is open. Please close it to save data."
            print(error_msg)
            return {'status': 'error', 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Error saving to Excel: {str(e)}"
            print(error_msg)
            return {'status': 'error', 'error': error_msg}
    
    def update_photo(self, index, new_subfolder, new_name):
        """
        Update photo information (for edit in preview)
        Returns: dict with status and message
        """
        if not (0 <= index < len(self.photos)):
            return {'status': 'error', 'message': 'Invalid photo index'}
        
        old_data = self.photos[index]
        old_path = Path(old_data['file_path'])
        
        # Check if file still exists
        if not old_path.exists():
            return {'status': 'error', 'message': 'Photo file not found'}
        
        # Create new path
        new_subfolder_path = self.project_folder / new_subfolder
        try:
            new_subfolder_path.mkdir(exist_ok=True)
        except Exception as e:
            return {'status': 'error', 'message': f'Cannot create subfolder: {e}'}
        
        new_filename = f"{new_name}.jpg"
        new_path = new_subfolder_path / new_filename
        
        # Move file if path changed
        if old_path != new_path:
            if new_path.exists():
                # Handle duplicate
                duplicate_result = self._handle_duplicate_check(new_path, new_name, new_subfolder_path)
                
                if duplicate_result['status'] == 'ask':
                    return {'status': 'duplicate', 'existing_path': str(new_path)}
                elif duplicate_result['status'] == 'new_path':
                    new_path = duplicate_result['path']
                    new_filename = new_path.name
                elif duplicate_result['status'] == 'replace':
                    self._move_to_trash(new_path)
            
            # Move file
            try:
                shutil.move(str(old_path), str(new_path))
            except Exception as e:
                return {'status': 'error', 'message': f'Cannot move file: {e}'}
        
        # Update data
        self.photos[index]['subfolder'] = new_subfolder
        self.photos[index]['name'] = new_name
        self.photos[index]['filename'] = new_filename
        self.photos[index]['file_path'] = str(new_path)
        
        # Rewrite Excel
        self._rewrite_excel()
        
        return {'status': 'success', 'data': self.photos[index]}
    
    def delete_photo(self, index):
        """
        Delete a photo (move to trash)
        Returns: dict with status
        """
        if not (0 <= index < len(self.photos)):
            return {'status': 'error', 'message': 'Invalid photo index'}
        
        photo = self.photos[index]
        file_path = Path(photo['file_path'])
        
        if file_path.exists():
            # Move to trash
            if self.config.get_setting("use_trash"):
                trash_path = self._move_to_trash(file_path)
                
                # Add to undo list (with limit)
                undo_limit = self.config.get_setting("undo_delete_limit", 10)
                self.deleted_photos.append({
                    'original_path': str(file_path),
                    'trash_path': str(trash_path),
                    'data': photo,
                    'index': index
                })
                
                # Limit undo history
                if len(self.deleted_photos) > undo_limit:
                    # Permanently delete oldest from trash
                    oldest = self.deleted_photos.pop(0)
                    oldest_trash = Path(oldest['trash_path'])
                    if oldest_trash.exists():
                        oldest_trash.unlink()
            else:
                # Permanent delete
                try:
                    file_path.unlink()
                except Exception as e:
                    return {'status': 'error', 'message': f'Cannot delete file: {e}'}
        
        # Remove from list
        deleted_data = self.photos.pop(index)
        
        # Rewrite Excel
        self._rewrite_excel()
        
        return {'status': 'success', 'deleted': deleted_data}
    
    def _move_to_trash(self, file_path):
        """Move file to trash folder"""
        trash_path = self.trash_folder / file_path.name
        
        # Handle duplicate in trash
        counter = 1
        while trash_path.exists():
            trash_path = self.trash_folder / f"{file_path.stem}_{counter}{file_path.suffix}"
            counter += 1
        
        try:
            shutil.move(str(file_path), str(trash_path))
            return trash_path
        except Exception as e:
            print(f"Error moving to trash: {e}")
            return None
    
    def undo_delete(self):
        """
        Undo last delete operation
        Returns: dict with status
        """
        if not self.deleted_photos:
            return {'status': 'error', 'message': 'No deletions to undo'}
        
        deleted = self.deleted_photos.pop()
        
        # Restore file
        trash_path = Path(deleted['trash_path'])
        original_path = Path(deleted['original_path'])
        
        if not trash_path.exists():
            return {'status': 'error', 'message': 'Deleted file not found in trash'}
        
        try:
            # Ensure parent directory exists
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(trash_path), str(original_path))
        except Exception as e:
            return {'status': 'error', 'message': f'Cannot restore file: {e}'}
        
        # Restore data at original position
        self.photos.insert(deleted.get('index', len(self.photos)), deleted['data'])
        self._rewrite_excel()
        
        return {'status': 'success', 'restored': deleted['data']}
    
    def _rewrite_excel(self):
        """Rewrite entire Excel file"""
        try:
            if self.photos:
                df = pd.DataFrame(self.photos)
                df = df[['Timestamp', 'Subfolder', 'Name', 'Filename', 'File Path']]
            else:
                df = pd.DataFrame(columns=['Timestamp', 'Subfolder', 'Name', 'Filename', 'File Path'])
            
            df.to_excel(self.config.session_file, index=False, engine='openpyxl')
            return True
        except Exception as e:
            print(f"Error rewriting Excel: {e}")
            return False
    
    def export_report(self, output_path):
        """
        Export current session to a new Excel file
        Returns: dict with status
        """
        if not self.photos:
            return {'status': 'error', 'message': 'No photos to export'}
        
        try:
            df = pd.DataFrame(self.photos)
            df = df[['Timestamp', 'Subfolder', 'Name', 'Filename', 'File Path']]
            df.to_excel(output_path, index=False, engine='openpyxl')
            return {'status': 'success', 'path': output_path, 'count': len(self.photos)}
        except Exception as e:
            return {'status': 'error', 'message': f'Export failed: {e}'}
    
    def end_session(self):
        """
        End current session (clear data and trash)
        Returns: dict with status
        """
        try:
            # Clear Excel
            self._init_excel()
            
            # Empty trash
            if self.trash_folder and self.trash_folder.exists():
                if self.config.get_setting("auto_empty_trash"):
                    # Delete all files in trash
                    for file in self.trash_folder.glob("*"):
                        try:
                            file.unlink()
                        except Exception as e:
                            print(f"Error deleting {file}: {e}")
            
            # Clear data
            self.photos = []
            self.deleted_photos = []
            self.pending_saves = 0
            
            # Clear active session
            self.config.clear_active_session()
            
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': f'Error ending session: {e}'}
    
    def _save_active_session(self):
        """Save active session for crash recovery"""
        session_data = {
            'project_folder': str(self.project_folder),
            'photo_count': len(self.photos),
            'last_activity': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.config.save_active_session(session_data)
    
    def get_photo_count(self):
        """Get total number of photos in session"""
        return len(self.photos)
    
    def get_subfolders(self):
        """Get list of unique subfolders used in session"""
        if not self.photos:
            return []
        return sorted(list(set(photo['subfolder'] for photo in self.photos)))
    
    def get_photo_by_index(self, index):
        """Get photo data by index"""
        if 0 <= index < len(self.photos):
            return self.photos[index]
        return None