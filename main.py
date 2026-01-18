"""
main.py - Shot Ledger Application Entry Point
Professional Photo Data Acquisition & Management System

Auto-detects real camera or uses mock camera for testing
"""

import sys
import os
import traceback

# ============================================
# CRITICAL FIX: Set environment variables FIRST
# ============================================
os.environ["TK_SILENCE_DEPRECATION"] = "1"
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

# Add current directory to Python path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)

print("\n" + "="*70)
print("SHOT LEDGER - Professional Photo Data Acquisition System")
print("="*70 + "\n")


def show_error_dialog(error_msg, detail=""):
    """Show error dialog"""
    try:
        import customtkinter as ctk
        from tkinter import messagebox
        
        root = ctk.CTk()
        root.withdraw()
        
        full_msg = f"Shot Ledger encountered an error:\n\n{error_msg}"
        if detail:
            full_msg += f"\n\nTechnical details:\n{detail[:500]}..."  # Limit detail length
        
        messagebox.showerror("Error", full_msg)
        root.destroy()
    except:
        print(f"ERROR: {error_msg}")
        if detail:
            print(f"Details: {detail}")


def main():
    """Main entry point for Shot Ledger"""
    
    try:
        print("[1/5] Importing libraries...")
        
        # Import customtkinter dengan DPI fix
        import customtkinter as ctk
        
        # FIX: Deactivate DPI awareness BEFORE creating any windows
        try:
            ctk.deactivate_automatic_dpi_awareness()
            print("   ✓ DPI awareness deactivated")
        except Exception as dpi_error:
            print(f"   ⚠ DPI fix warning: {dpi_error}")
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        print(f"   ✓ CustomTkinter v{ctk.__version__} initialized")
        
        # Import other modules
        print("[2/5] Loading application modules...")
        from config import Config
        from models import PhotoSession
        from ui.main_window import MainWindow
        
        print("   ✓ All modules loaded successfully")
        
        # Initialize configuration
        print("[3/5] Initializing configuration...")
        config = Config()
        print("   ✓ Configuration loaded")
        
        # Initialize session
        print("[4/5] Initializing photo session...")
        session = PhotoSession(config)
        print("   ✓ Session manager ready")
        
        # Create and run main window
        print("[5/5] Creating main application window...")
        app = MainWindow(config, session)
        
        print("\n" + "="*70)
        print("🎉 APPLICATION STARTED SUCCESSFULLY!")
        print("="*70)
        print("\nTips:")
        print("• Press SPACEBAR for quick photo capture")
        print("• Use Camera dropdown to switch cameras")
        print("• Press F12 for debug information")
        print("="*70 + "\n")
        
        # Start the application
        app.mainloop()
        
        print("\n" + "="*70)
        print("✅ APPLICATION CLOSED NORMALLY")
        print("="*70 + "\n")
        
    except ImportError as e:
        error_msg = f"Missing required library: {e}"
        detail = "Please run: pip install -r requirements.txt"
        show_error_dialog(error_msg, detail)
        print(f"\n❌ {error_msg}\n{detail}")
        sys.exit(1)
        
    except FileNotFoundError as e:
        error_msg = f"Required file not found: {e}"
        detail = "Make sure all required files are in place"
        show_error_dialog(error_msg, detail)
        print(f"\n❌ {error_msg}\n{detail}")
        sys.exit(1)
        
    except PermissionError as e:
        error_msg = f"Permission denied: {e}"
        detail = "Run as Administrator or check file permissions"
        show_error_dialog(error_msg, detail)
        print(f"\n❌ {error_msg}\n{detail}")
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        detail = traceback.format_exc()
        show_error_dialog(error_msg, "See console for full traceback")
        
        print("\n" + "="*70)
        print("❌ CRITICAL ERROR")
        print("="*70)
        print(f"Error: {error_msg}")
        print("\nFull Traceback:")
        print(detail)
        print("="*70)
        
        sys.exit(1)


if __name__ == "__main__":
    main()