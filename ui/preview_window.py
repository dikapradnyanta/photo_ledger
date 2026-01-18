"""
ui/preview_window.py - Photo Preview and Edit Window
Minimalist preview with edit capabilities (like Lightroom)
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from pathlib import Path
import os


class PreviewWindow(ctk.CTkToplevel):
    """Photo preview and edit window"""
    
    def __init__(self, parent, session, current_index):
        super().__init__(parent)
        
        self.session = session
        self.current_index = current_index
        self.result = None
        
        # Window setup
        self.title("Preview")
        
        # Get screen size for 80% default
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = int(screen_width * 0.8)
        height = int(screen_height * 0.8)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make resizable
        self.resizable(True, True)
        self.minsize(800, 600)
        
        self._create_ui()
        self._load_photo()
        
        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self.on_keep())
        self.bind("<Escape>", lambda e: self.on_cancel())
        self.bind("<Delete>", lambda e: self.on_delete())
        self.bind("<Left>", lambda e: self.navigate_prev())
        self.bind("<Right>", lambda e: self.navigate_next())
        
        # Modal
        self.transient(parent)
        self.grab_set()
        self.focus()
    
    def _create_ui(self):
        """Create preview UI"""
        # Top action bar
        top_bar = ctk.CTkFrame(self, height=65, corner_radius=0, fg_color=("#2b2b2b", "#1e1e1e"))
        top_bar.pack(fill="x", padx=0, pady=0)
        top_bar.pack_propagate(False)
        
        btn_container = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_container.pack(side="left", padx=20, pady=12)
        
        # Keep & Continue button
        self.keep_btn = ctk.CTkButton(
            btn_container,
            text="Keep & Continue",
            command=self.on_keep,
            width=160,
            height=41,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.keep_btn.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            btn_container,
            text="Delete",
            command=self.on_delete,
            width=100,
            height=41,
            font=ctk.CTkFont(size=13),
            fg_color="#f44336",
            hover_color="#da190b"
        )
        delete_btn.pack(side="left", padx=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_container,
            text="Cancel",
            command=self.on_cancel,
            width=100,
            height=41,
            font=ctk.CTkFont(size=13),
            fg_color="gray",
            hover_color="#5a5a5a"
        )
        cancel_btn.pack(side="left", padx=5)
        
        # Shortcut hints (right side)
        hints = ctk.CTkLabel(
            top_bar,
            text="ENTER: Keep  •  DEL: Delete  •  ESC: Cancel  •  ←/→: Navigate",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        hints.pack(side="right", padx=20)
        
        # Main content area
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Photo display area
        self.photo_frame = ctk.CTkFrame(content, fg_color=("#2b2b2b", "#1a1a1a"))
        self.photo_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.photo_label = ctk.CTkLabel(self.photo_frame, text="")
        self.photo_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Bottom info and controls
        bottom_panel = ctk.CTkFrame(content, height=110, corner_radius=8)
        bottom_panel.pack(fill="x", pady=0)
        bottom_panel.pack_propagate(False)
        
        # Edit fields
        edit_frame = ctk.CTkFrame(bottom_panel, fg_color="transparent")
        edit_frame.pack(side="left", fill="x", expand=True, padx=20, pady=15)
        
        # Subfolder field
        sub_container = ctk.CTkFrame(edit_frame, fg_color="transparent")
        sub_container.pack(side="left", padx=(0, 20))
        
        sub_label = ctk.CTkLabel(
            sub_container,
            text="Subfolder:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        )
        sub_label.pack(anchor="w", pady=(0, 5))
        
        self.subfolder_var = ctk.StringVar()
        self.subfolder_entry = ctk.CTkEntry(
            sub_container,
            textvariable=self.subfolder_var,
            width=200,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.subfolder_entry.pack()
        
        # Name field
        name_container = ctk.CTkFrame(edit_frame, fg_color="transparent")
        name_container.pack(side="left")
        
        name_label = ctk.CTkLabel(
            name_container,
            text="Name:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        self.name_var = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(
            name_container,
            textvariable=self.name_var,
            width=200,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.name_entry.pack()
        
        # File info (small text)
        self.file_label = ctk.CTkLabel(
            edit_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        self.file_label.pack(side="left", padx=(20, 0))
        
        # Navigation controls
        nav_frame = ctk.CTkFrame(bottom_panel, fg_color="transparent")
        nav_frame.pack(side="right", padx=20, pady=15)
        
        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            command=self.navigate_prev,
            width=50,
            height=35,
            font=ctk.CTkFont(size=16)
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.counter_label = ctk.CTkLabel(
            nav_frame,
            text="1/1",
            font=ctk.CTkFont(size=14),
            width=80
        )
        self.counter_label.pack(side="left", padx=10)
        
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            command=self.navigate_next,
            width=50,
            height=35,
            font=ctk.CTkFont(size=16)
        )
        self.next_btn.pack(side="left", padx=5)
    
    def _load_photo(self):
        """Load and display current photo"""
        photo = self.session.get_photo_by_index(self.current_index)
        
        if not photo:
            return
        
        # Update fields
        self.subfolder_var.set(photo['subfolder'])
        self.name_var.set(photo['name'])
        
        # Update file label
        self.file_label.configure(text=photo['filename'])
        
        # Update counter
        total = self.session.get_photo_count()
        self.counter_label.configure(text=f"{self.current_index + 1}/{total}")
        
        # Update navigation buttons
        self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_index < total - 1 else "disabled")
        
        # Load and display image
        file_path = Path(photo['file_path'])
        
        if file_path.exists():
            try:
                img = Image.open(file_path)
                
                # Get display area size
                display_width = self.photo_frame.winfo_width() - 20
                display_height = self.photo_frame.winfo_height() - 20
                
                # Fallback if window not yet rendered
                if display_width <= 1:
                    display_width = int(self.winfo_width() * 0.9)
                if display_height <= 1:
                    display_height = int(self.winfo_height() * 0.7)
                
                # Resize maintaining aspect ratio
                img.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
                
                # Display
                photo_img = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=img.size
                )
                self.photo_label.configure(image=photo_img, text="")
                self.photo_label.image = photo_img
                
            except Exception as e:
                self.photo_label.configure(
                    text=f"Error loading image:\n{e}",
                    image=None
                )
        else:
            self.photo_label.configure(
                text="Photo file not found",
                image=None
            )
    
    def navigate_prev(self):
        """Navigate to previous photo"""
        if self.current_index > 0:
            # Check for unsaved changes
            if self._has_changes():
                if not messagebox.askyesno(
                    "Unsaved Changes",
                    "You have unsaved changes. Discard them?",
                    parent=self
                ):
                    return
            
            self.current_index -= 1
            self._load_photo()
    
    def navigate_next(self):
        """Navigate to next photo"""
        if self.current_index < self.session.get_photo_count() - 1:
            # Check for unsaved changes
            if self._has_changes():
                if not messagebox.askyesno(
                    "Unsaved Changes",
                    "You have unsaved changes. Discard them?",
                    parent=self
                ):
                    return
            
            self.current_index += 1
            self._load_photo()
    
    def _has_changes(self):
        """Check if current photo has unsaved edits"""
        photo = self.session.get_photo_by_index(self.current_index)
        if not photo:
            return False
        
        return (
            self.subfolder_var.get() != photo['subfolder'] or
            self.name_var.get() != photo['name']
        )
    
    def on_keep(self):
        """Keep photo and continue"""
        new_subfolder = self.subfolder_var.get().strip()
        new_name = self.name_var.get().strip()
        
        if not new_subfolder:
            messagebox.showwarning("Missing Info", "Subfolder cannot be empty", parent=self)
            self.subfolder_entry.focus()
            return
        
        if not new_name:
            messagebox.showwarning("Missing Info", "Name cannot be empty", parent=self)
            self.name_entry.focus()
            return
        
        # Check if edited
        photo = self.session.get_photo_by_index(self.current_index)
        
        if new_subfolder != photo['subfolder'] or new_name != photo['name']:
            # Update photo
            result = self.session.update_photo(self.current_index, new_subfolder, new_name)
            
            if result['status'] == 'duplicate':
                # Handle duplicate
                handle = messagebox.askyesnocancel(
                    "Duplicate Name",
                    f"'{new_name}' already exists in {new_subfolder}/\n\n" +
                    "Yes: Replace old file\n" +
                    "No: Keep both (auto-rename)\n" +
                    "Cancel: Go back",
                    parent=self
                )
                
                if handle is None:  # Cancel
                    return
                elif handle:  # Replace
                    # Delete old file and update
                    self.session.update_photo(self.current_index, new_subfolder, new_name)
                else:  # Keep both - auto increment
                    # Find available name
                    counter = 2
                    new_name_inc = new_name
                    while True:
                        result = self.session.update_photo(self.current_index, new_subfolder, new_name_inc)
                        if result['status'] != 'duplicate':
                            break
                        new_name_inc = f"{new_name}_{counter}"
                        counter += 1
            
            elif result['status'] == 'error':
                messagebox.showerror("Error", result['message'], parent=self)
                return
        
        # Success - close and return
        self.result = {
            'action': 'keep',
            'index': self.current_index,
            'data': self.session.get_photo_by_index(self.current_index)
        }
        self.destroy()
    
    def on_delete(self):
        """Delete current photo"""
        photo = self.session.get_photo_by_index(self.current_index)
        
        if not photo:
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Delete Photo",
            f"Delete this photo?\n\n{photo['filename']}\n\n" +
            "You can restore from trash before session ends.",
            parent=self
        )
        
        if not confirm:
            return
        
        # Delete
        result = self.session.delete_photo(self.current_index)
        
        if result['status'] == 'success':
            # Photo deleted, move to next or close
            if self.session.get_photo_count() == 0:
                # No more photos
                self.result = {'action': 'deleted_all'}
                self.destroy()
            else:
                # Adjust index if needed
                if self.current_index >= self.session.get_photo_count():
                    self.current_index = self.session.get_photo_count() - 1
                
                # Reload
                self._load_photo()
                
                # Show undo notification
                self.show_undo_notification()
        else:
            messagebox.showerror("Error", result.get('message', 'Failed to delete'), parent=self)
    
    def show_undo_notification(self):
        """Show undo notification after delete"""
        # This would be implemented as a temporary overlay in the window
        # For now, just a simple approach
        pass
    
    def on_cancel(self):
        """Cancel without saving"""
        if self._has_changes():
            if not messagebox.askyesno(
                "Discard Changes?",
                "You have unsaved changes. Discard them?",
                parent=self
            ):
                return
        
        self.result = {'action': 'cancel'}
        self.destroy()
    
    def get_result(self):
        """Get the result of preview window"""
        return self.result