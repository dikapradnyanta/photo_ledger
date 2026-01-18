"""
utils/camera.py - Camera Management
Handles camera initialization, capture, and video feed
"""

import cv2
from PIL import Image, ImageDraw, ImageFont
import time
import numpy as np


class CameraHandler:
    """Manages camera operations"""
    
    def __init__(self):
        self.camera = None
        self.current_index = 0
        self.is_running = False
        self.backend = None
        self.placeholder_mode = False  # Flag for when camera not available
    
    def _create_placeholder_image(self, width=1920, height=1080, message="Camera Not Available"):
        """Create a placeholder image when camera is not available"""
        # Create blank image
        img = Image.new('RGB', (width, height), color=(40, 40, 40))
        draw = ImageDraw.Draw(img)
        
        # Try to load a nice font, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 80)
            detail_font = ImageFont.truetype("arial.ttf", 40)
            small_font = ImageFont.truetype("arial.ttf", 30)
        except:
            title_font = ImageFont.load_default()
            detail_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw camera icon (simple representation)
        icon_x, icon_y = width // 2, height // 2 - 150
        icon_size = 100
        
        # Camera body
        draw.rectangle(
            [icon_x - icon_size, icon_y - icon_size//2,
             icon_x + icon_size, icon_y + icon_size//2],
            fill=(100, 100, 100),
            outline=(150, 150, 150),
            width=5
        )
        
        # Lens
        draw.ellipse(
            [icon_x - icon_size//2, icon_y - icon_size//2,
             icon_x + icon_size//2, icon_y + icon_size//2],
            fill=(60, 60, 60),
            outline=(150, 150, 150),
            width=5
        )
        
        # Draw X over camera
        draw.line([icon_x - icon_size - 20, icon_y - icon_size,
                   icon_x + icon_size + 20, icon_y + icon_size],
                  fill=(255, 80, 80), width=8)
        draw.line([icon_x - icon_size - 20, icon_y + icon_size,
                   icon_x + icon_size + 20, icon_y - icon_size],
                  fill=(255, 80, 80), width=8)
        
        # Main message
        msg_bbox = draw.textbbox((0, 0), message, font=title_font)
        msg_width = msg_bbox[2] - msg_bbox[0]
        msg_x = (width - msg_width) // 2
        msg_y = icon_y + icon_size + 80
        
        draw.text((msg_x, msg_y), message, fill=(255, 100, 100), font=title_font)
        
        # Detail messages
        details = [
            "Possible causes:",
            "• Camera is being used by another application",
            "• Camera permission not granted",
            "• No camera connected to this computer",
            "• Camera driver issue",
            "",
            "Solutions:",
            "• Close apps using camera (Zoom, Teams, etc.)",
            "• Check Windows Settings > Privacy > Camera",
            "• Connect an external camera",
            "• Try restarting the application"
        ]
        
        detail_y = msg_y + 120
        for detail in details:
            if detail:  # Skip empty lines for spacing
                detail_bbox = draw.textbbox((0, 0), detail, font=small_font)
                detail_width = detail_bbox[2] - detail_bbox[0]
                detail_x = (width - detail_width) // 2
                
                # Highlight headers
                if detail.endswith(":"):
                    color = (255, 200, 100)
                else:
                    color = (200, 200, 200)
                
                draw.text((detail_x, detail_y), detail, fill=color, font=small_font)
            
            detail_y += 45
        
        # Bottom note
        note = f"Camera Index: {self.current_index}"
        note_bbox = draw.textbbox((0, 0), note, font=small_font)
        note_width = note_bbox[2] - note_bbox[0]
        note_x = (width - note_width) // 2
        
        draw.text((note_x, height - 80), note, fill=(150, 150, 150), font=small_font)
        
        # Convert PIL image to OpenCV format (BGR)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    def _try_backends(self, camera_index):
        """
        Try different camera backends in order
        Returns: (camera, backend_name) or (None, None)
        """
        # List of backends to try (Windows)
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),      # Usually most reliable on Windows
            (cv2.CAP_MSMF, "Media Foundation"), # Default but sometimes problematic
            (cv2.CAP_ANY, "Auto"),              # Let OpenCV decide
        ]
        
        for backend_id, backend_name in backends:
            print(f"Trying camera {camera_index} with {backend_name}...")
            
            try:
                camera = cv2.VideoCapture(camera_index, backend_id)
                
                # Wait a bit for camera to initialize
                time.sleep(0.3)
                
                if camera.isOpened():
                    # Test if we can actually read a frame
                    ret, frame = camera.read()
                    if ret and frame is not None:
                        print(f"✓ Success with {backend_name}")
                        return camera, backend_name
                    else:
                        print(f"✗ {backend_name} opened but can't read frames")
                        camera.release()
                else:
                    print(f"✗ {backend_name} failed to open")
                    camera.release()
                    
            except Exception as e:
                print(f"✗ {backend_name} error: {e}")
                continue
        
        return None, None
    
    def start(self, camera_index=0):
        """
        Start camera with given index
        Returns: dict with status
        """
        # Release previous camera if exists
        if self.camera:
            self.stop()
        
        print(f"\n{'='*50}")
        print(f"Starting camera {camera_index}...")
        print(f"{'='*50}")
        
        self.current_index = camera_index
        
        # Try different backends
        self.camera, self.backend = self._try_backends(camera_index)
        
        if not self.camera:
            # Camera not available - enter placeholder mode
            print(f"\n⚠️ Camera {camera_index} not available")
            print("Entering placeholder mode...")
            print(f"{'='*50}\n")
            
            self.placeholder_mode = True
            self.is_running = True
            
            # Return success but with warning
            return {
                'status': 'success',
                'index': camera_index,
                'backend': 'Placeholder Mode',
                'warning': 'Camera not available - showing placeholder'
            }
        
        # Camera available - normal mode
        self.placeholder_mode = False
        
        # Set camera properties for best quality
        try:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Get actual properties
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            print(f"\nCamera info:")
            print(f"  Backend: {self.backend}")
            print(f"  Resolution: {int(actual_width)}x{int(actual_height)}")
            print(f"  FPS: {actual_fps}")
            print(f"{'='*50}\n")
            
        except Exception as e:
            print(f"Warning: Could not set camera properties: {e}")
        
        self.is_running = True
        
        return {
            'status': 'success',
            'index': camera_index,
            'backend': self.backend
        }
    
    def stop(self):
        """Stop and release camera"""
        self.is_running = False
        self.placeholder_mode = False
        
        if self.camera:
            try:
                self.camera.release()
                print(f"Camera {self.current_index} released")
            except Exception as e:
                print(f"Error releasing camera: {e}")
            finally:
                self.camera = None
        
        return {'status': 'success'}
    
    def capture_frame(self):
        """
        Capture current frame
        Returns: dict with status and frame data
        """
        if self.placeholder_mode:
            # Return placeholder image
            frame = self._create_placeholder_image(
                message="Cannot Capture - Camera Not Available"
            )
            return {
                'status': 'success',
                'frame': frame,
                'placeholder': True
            }
        
        if not self.camera or not self.camera.isOpened():
            return {
                'status': 'error',
                'message': 'Camera not available'
            }
        
        # Try to capture frame with retries
        max_retries = 3
        for attempt in range(max_retries):
            ret, frame = self.camera.read()
            
            if ret and frame is not None:
                return {
                    'status': 'success',
                    'frame': frame,
                    'placeholder': False
                }
            
            # If failed, wait a bit and retry
            if attempt < max_retries - 1:
                print(f"Capture attempt {attempt + 1} failed, retrying...")
                time.sleep(0.1)
        
        return {
            'status': 'error',
            'message': 'Failed to capture frame after multiple attempts'
        }
    
    def get_preview_frame(self, display_width=900, display_height=700):
        """
        Get frame for preview display (resized)
        Returns: dict with PIL Image or error
        """
        if not self.is_running:
            return {'status': 'error', 'message': 'Camera not running'}
        
        # Placeholder mode - return static placeholder
        if self.placeholder_mode:
            placeholder = self._create_placeholder_image(1920, 1080)
            frame_rgb = cv2.cvtColor(placeholder, cv2.COLOR_BGR2RGB)
            
            # Calculate resize dimensions
            h, w = frame_rgb.shape[:2]
            aspect = w / h
            
            if aspect > display_width / display_height:
                new_width = display_width
                new_height = int(display_width / aspect)
            else:
                new_height = display_height
                new_width = int(display_height * aspect)
            
            frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
            img = Image.fromarray(frame_resized)
            
            return {
                'status': 'success',
                'image': img,
                'size': (new_width, new_height),
                'placeholder': True
            }
        
        # Normal mode - read from camera
        if not self.camera or not self.camera.isOpened():
            return {'status': 'error', 'message': 'Camera not available'}
        
        ret, frame = self.camera.read()
        
        if not ret or frame is None:
            return {'status': 'error', 'message': 'Failed to read frame'}
        
        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Calculate resize dimensions (maintain aspect ratio)
            h, w = frame_rgb.shape[:2]
            aspect = w / h
            
            if aspect > display_width / display_height:
                new_width = display_width
                new_height = int(display_width / aspect)
            else:
                new_height = display_height
                new_width = int(display_height * aspect)
            
            # Resize
            frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
            
            # Convert to PIL Image
            img = Image.fromarray(frame_resized)
            
            return {
                'status': 'success',
                'image': img,
                'size': (new_width, new_height),
                'placeholder': False
            }
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return {'status': 'error', 'message': f'Frame processing error: {e}'}
    
    def switch_camera(self, new_index):
        """
        Switch to different camera
        Returns: dict with status
        """
        print(f"\nSwitching from camera {self.current_index} to {new_index}...")
        self.stop()
        
        # Small delay to ensure camera is released
        time.sleep(0.2)
        
        return self.start(new_index)
    
    def is_available(self):
        """Check if camera is available and running"""
        return self.is_running  # Returns True even in placeholder mode
    
    def get_current_index(self):
        """Get current camera index"""
        return self.current_index
    
    def is_placeholder(self):
        """Check if running in placeholder mode"""
        return self.placeholder_mode