"""
ui/main_window.py - Main Application Window
Core UI for Shot Ledger application
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
import sys
import os

# We'll import these from their modules
from ui.folder_selector import FolderSelectorDialog
from ui.preview_window import PreviewWindow
from utils.camera import CameraHandler


class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self, config, session):
        super().__init__()
        
        self.config = config
        self.session = session
        self.camera = CameraHandler()
        self.camera_update_running = False
        
        # FIX: Atur DPI awareness sebelum window setup
        self._configure_dpi()
        
        # Window setup
        self.title("Shot Ledger")
        
        # Atur ukuran dan posisi window
        self.geometry("1400x820")
        
        # FIX: Pastikan window tidak mulai dalam state withdrawn atau iconic
        self.deiconify()
        
        # FIX: Angkat window ke depan dan fokus
        self.lift()
        self.focus_force()
        
        # Initialize project folder
        self.withdraw()  # Sembunyikan sementara untuk memilih folder
        
        # Show folder selector
        folder_dialog = FolderSelectorDialog(self, self.config)
        self.wait_window(folder_dialog)
        
        selected_folder = folder_dialog.get_selected_folder()
        
        if not selected_folder:
            # User cancelled
            self.destroy()
            return
        
        # Set project folder
        self.session.set_project_folder(selected_folder)
        self.session.load_from_excel()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Show main window
        self.deiconify()
        
        # FIX: Pastikan window muncul di taskbar dan Alt+Tab
        self._make_window_visible()
        
        # Create UI
        self._create_ui()
        
        # Start camera
        self._start_camera()
        
        # Window close handler
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Keyboard shortcuts
        self.bind("<space>", lambda e: self.capture_photo())
        
        # FIX: Binding untuk debugging
        self.bind("<F12>", lambda e: self._print_window_state())
    
    def _configure_dpi(self):
        """Configure DPI settings for Windows"""
        # Coba nonaktifkan DPI awareness jika menggunakan CustomTkinter
        try:
            ctk.deactivate_automatic_dpi_awareness()
        except:
            pass
        
        # Atur scaling untuk window
        self.tk.call('tk', 'scaling', 1.0)
    
    def _make_window_visible(self):
        """Make sure window is visible in taskbar and Alt+Tab"""
        # Pastikan window dalam state normal (bukan minimized)
        self.state('normal')
        
        # Angkat window ke depan
        self.lift()
        self.attributes('-topmost', True)
        self.update()
        self.attributes('-topmost', False)
        
        # Fokus ke window
        self.focus_force()
        
        # Update window manager
        self.update_idletasks()
    
    def _print_window_state(self):
        """Print window state for debugging"""
        print(f"Window state: {self.state()}")
        print(f"Window geometry: {self.geometry()}")
        print(f"Is mapped: {self.winfo_ismapped()}")
        print(f"Is viewable: {self.winfo_viewable()}")
    
    def _create_ui(self):
        """Create main UI layout"""
        # Configure grid columns for main content area
        self.grid_columnconfigure(0, weight=0)  # left panel - fixed width
        self.grid_columnconfigure(1, weight=1)  # right panel - expandable
        
        # LEFT PANEL - Controls
        left_panel = ctk.CTkFrame(self, width=420, corner_radius=0)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        left_panel.grid_propagate(False)
        
        # Title and status
        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.pack(pady=(25, 10), padx=30, fill="x")
        
        title = ctk.CTkLabel(
            header,
            text="📸 Shot Ledger",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack()
        
        # Session status
        self.session_status_label = ctk.CTkLabel(
            header,
            text=self._get_session_status_text(),
            font=ctk.CTkFont(size=12),
            text_color=self._get_session_status_color()
        )
        self.session_status_label.pack(pady=(8, 0))
        
        # Divider
        divider = ctk.CTkFrame(left_panel, height=2, fg_color="gray30")
        divider.pack(fill="x", padx=30, pady=15)
        
        # Camera selector
        cam_frame = self._create_input_section(left_panel, "Camera")
        
        self.camera_var = ctk.StringVar(value=f"Camera {self.config.get_camera_index()}")
        self.camera_combo = ctk.CTkComboBox(
            cam_frame,
            values=["Camera 0", "Camera 1", "Camera 2"],
            variable=self.camera_var,
            command=self._on_camera_change,
            height=42,
            font=ctk.CTkFont(size=13)
        )
        self.camera_combo.pack(fill="x")
        
        # Subfolder input
        sub_frame = self._create_input_section(left_panel, "Subfolder")
        
        self.subfolder_var = ctk.StringVar()
        self.subfolder_entry = ctk.CTkEntry(
            sub_frame,
            textvariable=self.subfolder_var,
            height=42,
            font=ctk.CTkFont(size=13),
            placeholder_text="e.g., Engineering, Marketing"
        )
        self.subfolder_entry.pack(fill="x")
        
        # Name input
        name_frame = self._create_input_section(left_panel, "Name")
        
        self.name_var = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(
            name_frame,
            textvariable=self.name_var,
            height=42,
            font=ctk.CTkFont(size=13),
            placeholder_text="e.g., John Doe, EMP-001"
        )
        self.name_entry.pack(fill="x")
        
        # Capture button
        self.capture_btn = ctk.CTkButton(
            left_panel,
            text="📸 CAPTURE",
            command=self.capture_photo,
            height=60,
            font=ctk.CTkFont(size=17, weight="bold"),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        self.capture_btn.pack(pady=20, padx=30, fill="x")
        
        # Camera status indicator
        self.camera_status_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        self.camera_status_frame.pack(pady=(0, 5))
        
        self.camera_status_label = ctk.CTkLabel(
            self.camera_status_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.camera_status_label.pack()
        
        # Shortcut hint
        hint = ctk.CTkLabel(
            left_panel,
            text="Press SPACEBAR for quick capture",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        hint.pack(pady=(5, 15))
        
        # Status message
        self.status_label = ctk.CTkLabel(
            left_panel,
            text="Ready to capture",
            font=ctk.CTkFont(size=13),
            text_color="green",
            wraplength=360
        )
        self.status_label.pack(pady=12, padx=30)
        
        # Bottom action buttons
        action_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        action_frame.pack(side="bottom", pady=25, padx=30, fill="x")
        
        export_btn = ctk.CTkButton(
            action_frame,
            text="📊 Export Report",
            command=self.export_report,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        export_btn.pack(fill="x", pady=3)
        
        end_btn = ctk.CTkButton(
            action_frame,
            text="🔄 End Session",
            command=self.end_session,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="gray",
            hover_color="#5a5a5a"
        )
        end_btn.pack(fill="x", pady=3)
        
        # RIGHT PANEL - Camera preview
        right_panel = ctk.CTkFrame(self, corner_radius=0)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        self.camera_label = ctk.CTkLabel(right_panel, text="Initializing camera...")
        self.camera_label.pack(expand=True, fill="both", padx=20, pady=20)
    
    def _create_input_section(self, parent, label_text):
        """Helper to create consistent input sections"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(pady=(5, 15), padx=30, fill="x")
        
        label = ctk.CTkLabel(
            container,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label.pack(anchor="w", pady=(0, 7))
        
        return container
    
    def _get_session_status_text(self):
        """Get session status text"""
        count = self.session.get_photo_count()
        if count == 0:
            return "⚪ No Active Session"
        else:
            return f"🟢 Session Active • {count} photo{'s' if count != 1 else ''}"
    
    def _get_session_status_color(self):
        """Get session status color"""
        return "green" if self.session.get_photo_count() > 0 else "gray"
    
    def _update_session_status(self):
        """Update session status label"""
        self.session_status_label.configure(
            text=self._get_session_status_text(),
            text_color=self._get_session_status_color()
        )
    
    def _on_subfolder_keypress(self, event):
        """Handle subfolder autocomplete"""
        subfolders = self.session.get_subfolders()
        if not subfolders:
            return
        current = self.subfolder_var.get()
        if current:
            matches = [s for s in subfolders if s.lower().startswith(current.lower())]
    
    def _start_camera(self):
        """Start camera feed"""
        camera_index = int(self.camera_var.get().split()[-1])
        result = self.camera.start(camera_index)
        
        if result['status'] == 'error':
            messagebox.showerror("Camera Error", result['message'])
            self.camera_label.configure(text="❌ Camera not available")
        else:
            if result.get('warning'):
                self._update_status(f"⚠️ {result['warning']}", "orange")
            
            self.camera_update_running = True
            self._update_camera_feed()
    
    def _update_camera_feed(self):
        """Update camera preview continuously"""
        if not self.camera_update_running:
            return
        
        result = self.camera.get_preview_frame(
            display_width=900,
            display_height=700
        )
        
        if result['status'] == 'success':
            img = result['image']
            size = result['size']
            
            photo = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=size
            )
            
            self.camera_label.configure(image=photo, text="")
            self.camera_label.image = photo
            
            if result.get('placeholder'):
                self.camera_status_label.configure(
                    text="⚠️ Camera Not Available - Showing Placeholder",
                    text_color="orange"
                )
                self.capture_btn.configure(state="disabled")
            else:
                self.camera_status_label.configure(
                    text="✓ Camera Active",
                    text_color="green"
                )
                self.capture_btn.configure(state="normal")
        
        if self.camera_update_running:
            self.after(30, self._update_camera_feed)
    
    def _on_camera_change(self, choice):
        """Handle camera change"""
        camera_index = int(choice.split()[-1])
        self.camera_update_running = False
        self.after(100, lambda: self._switch_camera(camera_index))
    
    def _switch_camera(self, index):
        """Switch to different camera"""
        result = self.camera.switch_camera(index)
        
        if result['status'] == 'error':
            messagebox.showerror("Camera Error", result['message'])
            self._update_status("❌ Camera switch failed", "red")
        else:
            self.config.set_camera_index(index)
            self.camera_update_running = True
            self._update_camera_feed()
            
            if result.get('warning'):
                self._update_status(f"⚠️ Camera {index} not available", "orange")
            else:
                self._update_status(f"✅ Switched to Camera {index}", "green")
    
    def capture_photo(self):
        """Capture photo from camera"""
        if self.camera.is_placeholder():
            messagebox.showwarning(
                "Camera Not Available",
                "Cannot capture photo - camera is not available.\n\n"
                "Please:\n"
                "• Close apps using the camera\n"
                "• Connect an external camera\n"
                "• Check camera permissions\n"
                "• Try switching camera index"
            )
            return
        
        subfolder = self.subfolder_var.get().strip()
        name = self.name_var.get().strip()
        
        if not subfolder:
            messagebox.showwarning("Missing Info", "Please enter Subfolder")
            self.subfolder_entry.focus()
            return
        
        if not name:
            messagebox.showwarning("Missing Info", "Please enter Name")
            self.name_entry.focus()
            return
        
        frame_result = self.camera.capture_frame()
        
        if frame_result['status'] == 'error':
            messagebox.showerror("Capture Error", frame_result['message'])
            return
        
        if frame_result.get('placeholder'):
            messagebox.showwarning("Cannot Capture", "Camera is not available - cannot capture photo.")
            return
        
        result = self.session.add_photo(subfolder, name, frame_result['frame'])
        
        if result['status'] == 'duplicate':
            self._handle_duplicate_photo(result, frame_result['frame'])
        elif result['status'] == 'error':
            messagebox.showerror("Error", result['message'])
            self._update_status(f"❌ {result['message']}", "red")
        elif result['status'] == 'success':
            if result.get('save_error'):
                self._update_status(f"⚠️ Photo saved, but: {result['save_error']}", "orange")
            self._show_preview(self.session.get_photo_count() - 1)
    
    def _handle_duplicate_photo(self, dup_info, frame):
        """Handle duplicate filename"""
        name = dup_info['name']
        subfolder = dup_info['subfolder']
        
        choice = messagebox.askyesnocancel(
            "Duplicate Name",
            f"'{name}' already exists in {subfolder}/\n\n" +
            "Yes: Replace old file\n" +
            "No: Keep both (auto-rename)\n" +
            "Cancel: Don't save",
            icon='warning'
        )
        
        if choice is None:
            self._update_status("❌ Capture cancelled", "gray")
            return
        
        old_setting = self.config.get_setting("duplicate_handling")
        
        if choice:
            self.config.set_setting("duplicate_handling", "replace")
            result = self.session.add_photo(subfolder, name, frame)
        else:
            self.config.set_setting("duplicate_handling", "auto_increment")
            result = self.session.add_photo(subfolder, name, frame)
        
        self.config.set_setting("duplicate_handling", old_setting)
        
        if result['status'] == 'success':
            self._show_preview(self.session.get_photo_count() - 1)
    
    def _show_preview(self, index):
        """Show preview window for captured photo"""
        preview = PreviewWindow(self, self.session, index)
        self.wait_window(preview)
        
        result = preview.get_result()
        
        if result and result['action'] == 'keep':
            self.name_var.set("")
            if self.config.get_setting("auto_focus_name"):
                self.name_entry.focus()
            photo = result['data']
            self._update_status(f"✅ Saved: {photo['filename']}", "green")
            self._update_session_status()
        elif result and result['action'] == 'deleted_all':
            self._update_status("🗑️ All photos deleted", "gray")
            self._update_session_status()
    
    def export_report(self):
        """Export session to Excel"""
        if self.session.get_photo_count() == 0:
            messagebox.showinfo("No Data", "No photos to export")
            return
        
        default_name = f"Report_{self.session.project_folder.name}.xlsx"
        
        file_path = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=default_name
        )
        
        if not file_path:
            return
        
        result = self.session.export_report(file_path)
        
        if result['status'] == 'success':
            messagebox.showinfo(
                "Export Successful",
                f"Exported {result['count']} photo(s) to:\n{file_path}"
            )
            self._update_status(f"📊 Exported {result['count']} photos", "green")
        else:
            messagebox.showerror("Export Failed", result['message'])
    
    def end_session(self):
        """End current session"""
        if self.session.get_photo_count() == 0:
            messagebox.showinfo("No Session", "No active session to end")
            return
        
        if self.config.get_setting("confirm_end_session"):
            confirm = messagebox.askyesnocancel(
                "End Session?",
                f"This will clear session data ({self.session.get_photo_count()} photos) and empty trash.\n\n" +
                "Photos in project folder will remain.\n\n" +
                "💡 Tip: Export report first if needed",
                icon='warning'
            )
            
            if not confirm:
                return
        
        result = self.session.end_session()
        
        if result['status'] == 'success':
            self._update_status("🔄 Session ended", "gray")
            self._update_session_status()
            messagebox.showinfo("Session Ended", "Session cleared successfully")
        else:
            messagebox.showerror("Error", result['message'])
    
    def _update_status(self, message, color):
        """Update status label"""
        self.status_label.configure(text=message, text_color=color)
    
    def _on_closing(self):
        """Handle window close"""
        if self.session.get_photo_count() > 0:
            on_exit = self.config.get_setting("on_exit")
            
            if on_exit == "ask":
                choice = messagebox.askyesnocancel(
                    "Unsaved Session",
                    f"You have {self.session.get_photo_count()} photos in current session.\n\n" +
                    "Yes: Export report first\n" +
                    "No: Keep session (can resume later)\n" +
                    "Cancel: Don't exit",
                    icon='warning'
                )
                
                if choice is None:
                    return
                elif choice:
                    self.export_report()
            
            elif on_exit == "end_session":
                if messagebox.askyesno(
                    "End Session?",
                    "End session and clear data before exit?",
                    icon='question'
                ):
                    self.session.end_session()
        
        self.camera_update_running = False
        self.camera.stop()
        self.destroy()