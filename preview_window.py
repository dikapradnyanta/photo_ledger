"""
preview_window.py - Preview Window with Navigation
"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import shutil
from pathlib import Path

class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, parent, session_photos, current_index):
        super().__init__(parent)
        
        self.session_photos = session_photos
        self.current_index = current_index
        self.result = None
        self.changes_made = []
        
        # Window setup
        self.title("Preview & Edit")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = int(screen_width * 0.85)
        height = int(screen_height * 0.85)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self._create_ui()
        self.load_photo()
        
        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self.on_keep())
        self.bind("<Escape>", lambda e: self.on_close())
        self.bind("<Delete>", lambda e: self.on_delete())
        self.bind("<Left>", lambda e: self.navigate_prev())
        self.bind("<Right>", lambda e: self.navigate_next())
        
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _create_ui(self):
        # Top bar
        top_bar = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=("#2b2b2b", "#1a1a1a"))
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)
        
        btn_container = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_container.pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(
            btn_container, text="✅ Keep & Continue",
            command=self.on_keep, width=160, height=40,
            fg_color="#4CAF50", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_container, text="🗑️ Delete",
            command=self.on_delete, width=120, height=40, fg_color="#f44336"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_container, text="← Back",
            command=self.on_close, width=100, height=40, fg_color="gray"
        ).pack(side="left", padx=5)
        
        # Photo display
        photo_frame = ctk.CTkFrame(self, fg_color="black")
        photo_frame.pack(expand=True, fill="both")
        
        self.photo_label = ctk.CTkLabel(photo_frame, text="")
        self.photo_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Bottom panel
        bottom_panel = ctk.CTkFrame(self, height=140, corner_radius=0, fg_color=("#2b2b2b", "#1a1a1a"))
        bottom_panel.pack(fill="x")
        bottom_panel.pack_propagate(False)
        
        # Edit fields
        edit_frame = ctk.CTkFrame(bottom_panel, fg_color="transparent")
        edit_frame.pack(pady=15, padx=40, fill="x")
        
        left_edit = ctk.CTkFrame(edit_frame, fg_color="transparent")
        left_edit.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            left_edit, text="📁 Subfolder:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        self.div_var = ctk.StringVar()
        ctk.CTkEntry(
            left_edit, textvariable=self.div_var,
            width=220, height=35, font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 30))
        
        ctk.CTkLabel(
            left_edit, text="👤 Name:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        self.name_var = ctk.StringVar()
        ctk.CTkEntry(
            left_edit, textvariable=self.name_var,
            width=220, height=35, font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        ctk.CTkButton(
            left_edit, text="💾 Apply",
            command=self.apply_changes, width=110, height=35,
            fg_color="#FF9800"
        ).pack(side="left", padx=(20, 0))
        
        # Navigation
        nav_frame = ctk.CTkFrame(bottom_panel, fg_color="transparent")
        nav_frame.pack(pady=(0, 15))
        
        self.prev_btn = ctk.CTkButton(
            nav_frame, text="◀ Prev",
            command=self.navigate_prev, width=100, height=35
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.counter_label = ctk.CTkLabel(
            nav_frame, text="",
            font=ctk.CTkFont(size=14, weight="bold"), width=100
        )
        self.counter_label.pack(side="left", padx=20)
        
        self.next_btn = ctk.CTkButton(
            nav_frame, text="Next ▶",
            command=self.navigate_next, width=100, height=35
        )
        self.next_btn.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            nav_frame, text="  •  ← → keys  •  Enter=keep  •  Del=remove",
            font=ctk.CTkFont(size=10), text_color="gray"
        ).pack(side="left", padx=20)
    
    def load_photo(self):
        if 0 <= self.current_index < len(self.session_photos):
            photo_info = self.session_photos[self.current_index]
            
            self.div_var.set(photo_info['division'])
            self.name_var.set(photo_info['name'])
            self.counter_label.configure(text=f"{self.current_index + 1} / {len(self.session_photos)}")
            
            self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
            self.next_btn.configure(state="normal" if self.current_index < len(self.session_photos) - 1 else "disabled")
            
            if os.path.exists(photo_info['path']):
                try:
                    img = Image.open(photo_info['path'])
                    display_width = int(self.winfo_width() * 0.95)
                    display_height = int(self.winfo_height() * 0.60)
                    img.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
                    
                    photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                    self.photo_label.configure(image=photo, text="")
                    self.photo_label.image = photo
                except Exception as e:
                    self.photo_label.configure(text=f"❌ Error: {e}")
            else:
                self.photo_label.configure(text="❌ Photo not found")
    
    def navigate_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_photo()
    
    def navigate_next(self):
        if self.current_index < len(self.session_photos) - 1:
            self.current_index += 1
            self.load_photo()
    
    def apply_changes(self):
        new_div = self.div_var.get().strip()
        new_name = self.name_var.get().strip()
        
        if not new_div or not new_name:
            messagebox.showwarning("Invalid", "Both fields required")
            return
        
        photo_info = self.session_photos[self.current_index]
        old_path = Path(photo_info['path'])
        
        if new_div == photo_info['division'] and new_name == photo_info['name']:
            messagebox.showinfo("No Changes", "Nothing to change")
            return
        
        new_folder = old_path.parent.parent / new_div
        new_filename = f"{new_name}.jpg"
        new_path = new_folder / new_filename
        
        new_folder.mkdir(exist_ok=True)
        
        try:
            if old_path.exists():
                shutil.move(str(old_path), str(new_path))
            
            photo_info['division'] = new_div
            photo_info['name'] = new_name
            photo_info['path'] = str(new_path)
            
            self.changes_made.append({
                'index': self.current_index,
                'action': 'edit',
                'division': new_div,
                'name': new_name
            })
            
            messagebox.showinfo("Success", f"Updated: {new_div} / {new_name}")
            self.load_photo()
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
    
    def on_delete(self):
        if not messagebox.askyesno("Delete?", "Delete this photo?"):
            return
        
        photo_info = self.session_photos[self.current_index]
        file_path = Path(photo_info['path'])
        
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
                return
        
        self.changes_made.append({
            'index': self.current_index,
            'action': 'delete'
        })
        
        self.session_photos.pop(self.current_index)
        
        if self.current_index >= len(self.session_photos):
            self.current_index = len(self.session_photos) - 1
        
        if len(self.session_photos) == 0:
            messagebox.showinfo("Empty", "All photos deleted")
            self.result = {'action': 'all_deleted', 'changes': self.changes_made}
            self.destroy()
        else:
            self.load_photo()
    
    def on_keep(self):
        self.result = {'action': 'keep', 'changes': self.changes_made}
        self.destroy()
    
    def on_close(self):
        self.result = {'action': 'close', 'changes': self.changes_made}
        self.destroy()