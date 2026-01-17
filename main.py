"""
main.py - Main Application
RUN THIS FILE!
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import cv2
from PIL import Image
import pandas as pd
from datetime import datetime
import os
import shutil
from pathlib import Path
import threading

from config import Config
from dialogs import FolderSelectorDialog
from preview_window import PreviewWindow

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ShotLedgerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Shot Ledger")
        self.geometry("1400x800")
        
        self.config = Config()
        self.camera = None
        self.camera_running = False
        self.session_photos = []
        
        # Select folder
        self.withdraw()
        dialog = FolderSelectorDialog(self, self.config)
        self.wait_window(dialog)
        
        if not dialog.selected_folder:
            self.destroy()
            return
        
        self.project_folder = Path(dialog.selected_folder)
        self.deiconify()
        
        self._init_session()
        self._create_ui()
        self._start_camera()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _init_session(self):
        """Initialize or restore session"""
        if self.config.session_file.exists():
            try:
                df = pd.read_excel(self.config.session_file)
                for _, row in df.iterrows():
                    self.session_photos.append({
                        'path': row['Path'],
                        'division': row['Subfolder'],
                        'name': row['Name'],
                        'timestamp': row['Timestamp']
                    })
            except:
                pass
        
        if not self.config.session_file.exists():
            df = pd.DataFrame(columns=["Timestamp", "Subfolder", "Name", "Filename", "Path"])
            df.to_excel(self.config.session_file, index=False)
    
    def _create_ui(self):
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # LEFT PANEL
        left = ctk.CTkFrame(self, width=400, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)
        
        ctk.CTkLabel(
            left, text="📸 Shot Ledger",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 5))
        
        self.session_label = ctk.CTkLabel(
            left, text=f"🟢 Session: {len(self.session_photos)} photos",
            font=ctk.CTkFont(size=12),
            text_color="green" if self.session_photos else "gray"
        )
        self.session_label.pack(pady=5)
        
        ctk.CTkLabel(
            left, text=f"📁 {self.project_folder.name}",
            font=ctk.CTkFont(size=11), text_color="gray"
        ).pack(pady=(0, 20))
        
        # Inputs
        ctk.CTkLabel(
            left, text="Subfolder",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
        ).pack(padx=30, anchor="w")
        
        self.subfolder_var = ctk.StringVar()
        ctk.CTkEntry(
            left, textvariable=self.subfolder_var,
            height=40, placeholder_text="e.g., Engineering"
        ).pack(pady=(5, 15), padx=30, fill="x")
        
        ctk.CTkLabel(
            left, text="Name",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
        ).pack(padx=30, anchor="w")
        
        self.name_var = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(
            left, textvariable=self.name_var,
            height=40, placeholder_text="e.g., John Doe"
        )
        self.name_entry.pack(pady=(5, 20), padx=30, fill="x")
        
        # Capture button
        self.capture_btn = ctk.CTkButton(
            left, text="📸 CAPTURE",
            command=self.capture_photo, height=55,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2196F3"
        )
        self.capture_btn.pack(pady=10, padx=30, fill="x")
        
        ctk.CTkLabel(
            left, text="Press SPACE to capture",
            font=ctk.CTkFont(size=10), text_color="gray"
        ).pack()
        
        self.status_label = ctk.CTkLabel(
            left, text="✅ Ready",
            font=ctk.CTkFont(size=12), text_color="green"
        )
        self.status_label.pack(pady=20)
        
        # Review button (if photos exist)
        self.review_btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.review_btn_frame.pack(pady=5, padx=30, fill="x")
        self._update_review_button()
        
        # Bottom buttons
        bottom = ctk.CTkFrame(left, fg_color="transparent")
        bottom.pack(side="bottom", pady=20, padx=30, fill="x")
        
        ctk.CTkButton(
            bottom, text="📊 Export Excel",
            command=self.export_report, height=35
        ).pack(fill="x", pady=2)
        
        ctk.CTkButton(
            bottom, text="🔄 End Session",
            command=self.end_session, height=35, fg_color="gray"
        ).pack(fill="x", pady=2)
        
        # RIGHT PANEL - Camera
        right = ctk.CTkFrame(self, corner_radius=0, fg_color="black")
        right.grid(row=0, column=1, sticky="nsew")
        
        self.camera_label = ctk.CTkLabel(right, text="")
        self.camera_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Keyboard shortcuts
        self.bind("<space>", lambda e: self.capture_photo())
    
    def _start_camera(self):
        self.camera = cv2.VideoCapture(0)
        if self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.camera_running = True
            self._update_feed()
        else:
            messagebox.showerror("Camera Error", "Cannot access camera")
    
    def _update_feed(self):
        if self.camera_running and self.camera:
            ret, frame = self.camera.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w = rgb.shape[:2]
                
                max_w, max_h = 900, 650
                scale = min(max_w/w, max_h/h)
                new_w, new_h = int(w*scale), int(h*scale)
                
                resized = cv2.resize(rgb, (new_w, new_h))
                img = Image.fromarray(resized)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))
                
                self.camera_label.configure(image=photo)
                self.camera_label.image = photo
            
            self.after(30, self._update_feed)
    
    def capture_photo(self):
        subfolder = self.subfolder_var.get().strip()
        name = self.name_var.get().strip()
        
        if not subfolder or not name:
            messagebox.showwarning("Missing Info", "Enter Subfolder and Name")
            return
        
        if not self.camera or not self.camera.isOpened():
            messagebox.showerror("Error", "Camera not available")
            return
        
        ret, frame = self.camera.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture")
            return
        
        # Save photo
        folder = self.project_folder / subfolder
        folder.mkdir(exist_ok=True)
        
        timestamp = datetime.now()
        filename = f"{name}.jpg"
        filepath = folder / filename
        
        # Handle duplicates
        counter = 1
        while filepath.exists():
            filename = f"{name}_{counter}.jpg"
            filepath = folder / filename
            counter += 1
        
        cv2.imwrite(str(filepath), frame)
        
        # Add to session
        photo_info = {
            'path': str(filepath),
            'division': subfolder,
            'name': name,
            'timestamp': timestamp
        }
        self.session_photos.append(photo_info)
        
        # Log to Excel
        threading.Thread(target=self._log_excel, args=(photo_info,), daemon=True).start()
        
        # Update UI
        self._update_status(f"✅ Captured: {filename}", "green")
        self._update_session_label()
        self._update_review_button()
        
        # Clear name for next
        self.name_var.set("")
        self.name_entry.focus()
        
        # Auto-open preview
        self.after(100, lambda: self.open_review_mode(len(self.session_photos) - 1))
    
    def open_review_mode(self, start_index=0):
        """Open preview window"""
        if not self.session_photos:
            messagebox.showinfo("No Photos", "No photos to review")
            return
        
        preview = PreviewWindow(self, self.session_photos, start_index)
        self.wait_window(preview)
        
        # Handle changes
        if preview.result and preview.result.get('changes'):
            self._rebuild_excel()
        
        self._update_session_label()
        self._update_review_button()
    
    def _log_excel(self, info):
        """Log photo to Excel"""
        try:
            data = {
                "Timestamp": [info['timestamp']],
                "Subfolder": [info['division']],
                "Name": [info['name']],
                "Filename": [Path(info['path']).name],
                "Path": [info['path']]
            }
            
            df_new = pd.DataFrame(data)
            
            if self.config.session_file.exists():
                df = pd.read_excel(self.config.session_file)
                df = pd.concat([df, df_new], ignore_index=True)
            else:
                df = df_new
            
            df.to_excel(self.config.session_file, index=False)
        except Exception as e:
            print(f"Excel log error: {e}")
    
    def _rebuild_excel(self):
        """Rebuild Excel from session_photos"""
        try:
            if not self.session_photos:
                df = pd.DataFrame(columns=["Timestamp", "Subfolder", "Name", "Filename", "Path"])
            else:
                data = {
                    "Timestamp": [p['timestamp'] for p in self.session_photos],
                    "Subfolder": [p['division'] for p in self.session_photos],
                    "Name": [p['name'] for p in self.session_photos],
                    "Filename": [Path(p['path']).name for p in self.session_photos],
                    "Path": [p['path'] for p in self.session_photos]
                }
                df = pd.DataFrame(data)
            
            df.to_excel(self.config.session_file, index=False)
        except Exception as e:
            print(f"Rebuild Excel error: {e}")
    
    def _update_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)
    
    def _update_session_label(self):
        count = len(self.session_photos)
        self.session_label.configure(
            text=f"🟢 Session: {count} photo{'s' if count != 1 else ''}",
            text_color="green" if count > 0 else "gray"
        )
    
    def _update_review_button(self):
        """Show/hide review button"""
        for widget in self.review_btn_frame.winfo_children():
            widget.destroy()
        
        if len(self.session_photos) > 0:
            ctk.CTkButton(
                self.review_btn_frame,
                text=f"🖼️ Review {len(self.session_photos)} Photos",
                command=self.open_review_mode,
                height=40, fg_color="#9C27B0"
            ).pack(fill="x")
    
    def export_report(self):
        """Export Excel report"""
        if not self.session_photos:
            messagebox.showinfo("No Data", "No photos to export")
            return
        
        file = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=f"Report_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        )
        
        if file:
            try:
                shutil.copy(self.config.session_file, file)
                messagebox.showinfo("Success", f"Exported to:\n{file}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{e}")
    
    def end_session(self):
        """End current session"""
        if not messagebox.askyesno("End Session?", 
            "End session and clear photo log?"):
            return
        
        self.session_photos.clear()
        
        if self.config.session_file.exists():
            os.remove(self.config.session_file)
        
        self._init_session()
        self._update_session_label()
        self._update_review_button()
        self._update_status("Session ended", "gray")
    
    def _on_closing(self):
        """Clean up on close"""
        if self.camera:
            self.camera_running = False
            self.camera.release()
        self.destroy()

if __name__ == "__main__":
    app = ShotLedgerApp()
    app.mainloop()