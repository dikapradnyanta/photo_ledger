"""
dialogs.py - Dialog Windows
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

class FolderSelectorDialog(ctk.CTkToplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.selected_folder = None
        
        self.title("Select Project Folder")
        self.geometry("600x500")
        x = (self.winfo_screenwidth() - 600) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"600x500+{x}+{y}")
        
        self._create_ui()
        self.transient(parent)
        self.grab_set()
    
    def _create_ui(self):
        # Title
        ctk.CTkLabel(
            self, text="📸 Shot Ledger",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            self, text="Select Project Folder",
            font=ctk.CTkFont(size=16), text_color="gray"
        ).pack(pady=(0, 30))
        
        # Path entry
        self.folder_var = ctk.StringVar(value=self.config.settings.get("last_project", ""))
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(pady=10, padx=40, fill="x")
        
        ctk.CTkEntry(
            path_frame, textvariable=self.folder_var, height=45
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            path_frame, text="Browse",
            command=self.browse_folder, width=100, height=45
        ).pack(side="right")
        
        # Recent projects
        if self.config.settings.get("recent_projects"):
            ctk.CTkLabel(
                self, text="Recent:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(pady=(20, 5), padx=40, anchor="w")
            
            for project in self.config.settings["recent_projects"][:5]:
                ctk.CTkButton(
                    self, text=f"📁 {project}",
                    command=lambda p=project: self.folder_var.set(p),
                    fg_color="transparent", anchor="w"
                ).pack(fill="x", padx=40, pady=2)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=30, padx=40, fill="x")
        
        ctk.CTkButton(
            btn_frame, text="Cancel",
            command=self.destroy, fg_color="gray",
            width=120, height=40
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            btn_frame, text="Open",
            command=self.on_open, width=150, height=40
        ).pack(side="right")
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
    
    def on_open(self):
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showwarning("No Folder", "Please select a folder")
            return
        
        if not os.path.exists(folder):
            if messagebox.askyesno("Create?", f"Create folder?\n{folder}"):
                os.makedirs(folder, exist_ok=True)
            else:
                return
        
        self.selected_folder = folder
        self.config.add_recent_project(folder)
        self.destroy()