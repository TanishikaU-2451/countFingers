"""
FPS (Frames Per Second) counter for performance monitoring.
"""

import time


class FPSCounter:
    """Calculate and track FPS for real-time performance monitoring."""
    
    def __init__(self, window_size=30):
        """
        Initialize FPS counter.
        
        Args:
            window_size: Number of frames to average for FPS calculation
        """
        self.window_size = window_size
        self.frame_times = []
        self.last_frame_time = time.time()
        self.fps = 0
        self.total_frames = 0
    
    def update(self):
        """Update FPS counter with current frame."""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        
        # Store frame time
        self.frame_times.append(frame_time)
        
        # Keep only recent frames for averaging
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        
        # Calculate average FPS
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            if avg_frame_time > 0:
                self.fps = 1.0 / avg_frame_time
        
        self.total_frames += 1
        self.last_frame_time = current_time
    
    def get_fps(self):
        """Return current FPS value."""
        return self.fps
    
    def get_inference_time(self):
        """Return average frame time in milliseconds."""
        if self.frame_times:
            avg_time = sum(self.frame_times) / len(self.frame_times)
            return avg_time * 1000  # Convert to milliseconds
        return 0.0
    
    def get_total_frames(self):
        """Return total number of frames processed."""
        return self.total_frames
    
    def format_fps(self):
        """Return formatted FPS string."""
        return f"FPS: {self.fps:.1f}"
    
    def format_inference_time(self):
        """Return formatted inference time string."""
        return f"Time: {self.get_inference_time():.2f}ms"
