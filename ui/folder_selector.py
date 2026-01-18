"""
ui/folder_selector.py - Project Folder Selection Dialog
Startup dialog for selecting project folder (like VS Code)
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os


class FolderSelectorDialog(ctk.CTkToplevel):
    """Startup dialog for selecting project folder"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        
        self.config = config
        self.selected_folder = None
        
        # Window setup
        self.title("Shot Ledger - Select Project Folder")
        self.geometry("650x500")
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"650x500+{x}+{y}")
        
        self._create_ui()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Focus on path entry if last project exists
        if self.config.settings.get("last_project"):
            self.path_entry.focus()
    
    def _create_ui(self):
        """Create dialog UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(40, 20), padx=40, fill="x")
        
        title = ctk.CTkLabel(
            header_frame,
            text="📸 Shot Ledger",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Select Project Folder",
            font=ctk.CTkFont(size=18),
            text_color="gray"
        )
        subtitle.pack(pady=(5, 0))
        
        # Info text
        info = ctk.CTkLabel(
            self,
            text="All photos will be saved in this folder",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        info.pack(pady=(0, 25))
        
        # Folder path input
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(pady=15, padx=40, fill="x")
        
        path_label = ctk.CTkLabel(
            path_frame,
            text="Folder Path:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        path_label.pack(anchor="w", pady=(0, 5))
        
        input_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        input_frame.pack(fill="x")
        
        self.folder_var = ctk.StringVar(value=self.config.settings.get("last_project", ""))
        
        self.path_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.folder_var,
            height=45,
            font=ctk.CTkFont(size=13),
            placeholder_text="Select or type folder path..."
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Browse button
        browse_btn = ctk.CTkButton(
            input_frame,
            text="📂 Browse",
            command=self.browse_folder,
            width=110,
            height=45,
            font=ctk.CTkFont(size=13)
        )
        browse_btn.pack(side="right")
        
        # Recent projects section
        if self.config.settings.get("recent_projects"):
            recent_frame = ctk.CTkFrame(self)
            recent_frame.pack(pady=20, padx=40, fill="both", expand=True)
            
            recent_label = ctk.CTkLabel(
                recent_frame,
                text="Recent Folders:",
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            recent_label.pack(pady=(15, 10), padx=15, anchor="w")
            
            # Scrollable recent list
            recent_scroll = ctk.CTkScrollableFrame(
                recent_frame,
                fg_color="transparent"
            )
            recent_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            for project in self.config.settings["recent_projects"][:5]:
                self._create_recent_item(recent_scroll, project)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=25, padx=40, fill="x")
        
        # Quick open button (if last project exists)
        if self.config.settings.get("last_project"):
            quick_btn = ctk.CTkButton(
                btn_frame,
                text="📂 Open Last Project",
                command=self.open_last,
                height=45,
                font=ctk.CTkFont(size=14),
                fg_color="#2196F3",
                hover_color="#1976D2"
            )
            quick_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.on_cancel,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            hover_color="#5a5a5a",
            width=120
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # Open button
        open_btn = ctk.CTkButton(
            btn_frame,
            text="Open Project",
            command=self.on_open,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            width=150
        )
        open_btn.pack(side="right")
        
        # Bind Enter key to open
        self.bind("<Return>", lambda e: self.on_open())
        self.bind("<Escape>", lambda e: self.on_cancel())
    
    def _create_recent_item(self, parent, project_path):
        """Create a recent project item button"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", pady=3, padx=5)
        
        # Extract folder name for display
        folder_name = os.path.basename(project_path)
        
        btn = ctk.CTkButton(
            item_frame,
            text=f"📁 {folder_name}",
            command=lambda: self.select_recent(project_path),
            anchor="w",
            fg_color="transparent",
            hover_color=("#3a3a3a", "#2a2a2a"),
            height=35,
            font=ctk.CTkFont(size=12)
        )
        btn.pack(side="left", fill="x", expand=True)
        
        # Path label (smaller, gray)
        path_label = ctk.CTkLabel(
            item_frame,
            text=project_path,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        path_label.pack(side="left", padx=(10, 0))
    
    def browse_folder(self):
        """Open folder browser dialog"""
        initial_dir = self.folder_var.get() or os.path.expanduser("~")
        
        folder = filedialog.askdirectory(
            title="Select Project Folder",
            initialdir=initial_dir
        )
        
        if folder:
            self.folder_var.set(folder)
            self.path_entry.focus()
    
    def select_recent(self, path):
        """Select a recent project"""
        self.folder_var.set(path)
        self.on_open()
    
    def open_last(self):
        """Open last used project"""
        self.folder_var.set(self.config.settings["last_project"])
        self.on_open()
    
    def on_open(self):
        """Handle open project action"""
        folder = self.folder_var.get().strip()
        
        if not folder:
            messagebox.showwarning(
                "No Folder Selected",
                "Please select or enter a project folder path.",
                parent=self
            )
            self.path_entry.focus()
            return
        
        # Validate and create if needed
        if not os.path.exists(folder):
            create = messagebox.askyesno(
                "Create Folder?",
                f"Folder does not exist:\n\n{folder}\n\nCreate it now?",
                parent=self
            )
            if create:
                try:
                    os.makedirs(folder, exist_ok=True)
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Cannot create folder:\n{e}",
                        parent=self
                    )
                    return
            else:
                return
        
        # Verify it's a valid directory
        if not os.path.isdir(folder):
            messagebox.showerror(
                "Invalid Path",
                "Selected path is not a valid folder.",
                parent=self
            )
            return
        
        # Success - store and close
        self.selected_folder = folder
        self.config.add_recent_project(folder)
        self.destroy()
    
    def on_cancel(self):
        """Handle cancel action"""
        self.selected_folder = None
        self.destroy()
    
    def get_selected_folder(self):
        """Get the selected folder path"""
        return self.selected_folder