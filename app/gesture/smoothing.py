"""
Temporal smoothing utilities for stable gesture output.

Stabilizes noisy detections using moving average and history tracking.
"""

from collections import deque
from typing import Optional, Dict, List
from app.config import settings


class MovingAverageSmoother:
    """
    Smooths numeric values using moving average over a time window.
    
    Useful for stabilizing finger counts and gesture classifications
    that may vary frame-to-frame due to lighting or hand movement.
    """
    
    def __init__(self, window_size: int = settings.SMOOTHING_WINDOW_SIZE):
        """
        Initialize moving average smoother.
        
        Args:
            window_size: Number of frames to average
        """
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
    
    def update(self, value: float) -> float:
        """
        Add new value and return smoothed average.
        
        Args:
            value: New value to add
        
        Returns:
            Float: Smoothed average value
        """
        self.values.append(value)
        if self.values:
            return sum(self.values) / len(self.values)
        return value
    
    def get_smooth(self) -> float:
        """Get current smoothed value without updating."""
        if self.values:
            return sum(self.values) / len(self.values)
        return 0.0
    
    def reset(self):
        """Clear history."""
        self.values.clear()


class FingerCountSmoother:
    """
    Specialized smoother for finger counts that enforces integer output.
    
    Provides stabilized integer finger counts by rounding the moving average.
    """
    
    def __init__(self, window_size: int = settings.SMOOTHING_WINDOW_SIZE):
        """Initialize finger count smoother."""
        self.smoother = MovingAverageSmoother(window_size)
    
    def update(self, count: int) -> int:
        """
        Update with new finger count.
        
        Args:
            count: Number of fingers extended (0-5)
        
        Returns:
            Int: Smoothed finger count (rounded to nearest integer)
        """
        smoothed = self.smoother.update(float(count))
        return round(smoothed)
    
    def get_smooth(self) -> int:
        """Get current smoothed finger count."""
        return round(self.smoother.get_smooth())
    
    def reset(self):
        """Clear history."""
        self.smoother.reset()


class GestureStateTracker:
    """
    Tracks gesture state over time with timeout-based removal.
    
    Removes gesture output when hand disappears for more than
    HAND_TIMEOUT_FRAMES consecutive frames.
    """
    
    def __init__(self, timeout_frames: int = settings.HAND_TIMEOUT_FRAMES):
        """
        Initialize gesture state tracker.
        
        Args:
            timeout_frames: Frames to wait before removing gesture
        """
        self.timeout_frames = timeout_frames
        self.states: Dict[str, dict] = {
            'left': {'data': None, 'missing_frames': 0},
            'right': {'data': None, 'missing_frames': 0},
        }
    
    def update_left(self, gesture_data: Optional[dict]):
        """
        Update left hand gesture state.
        
        Args:
            gesture_data: Gesture data dict or None if hand not detected
        """
        if gesture_data is not None:
            self.states['left']['data'] = gesture_data
            self.states['left']['missing_frames'] = 0
        else:
            self.states['left']['missing_frames'] += 1
            if self.states['left']['missing_frames'] > self.timeout_frames:
                self.states['left']['data'] = None
    
    def update_right(self, gesture_data: Optional[dict]):
        """
        Update right hand gesture state.
        
        Args:
            gesture_data: Gesture data dict or None if hand not detected
        """
        if gesture_data is not None:
            self.states['right']['data'] = gesture_data
            self.states['right']['missing_frames'] = 0
        else:
            self.states['right']['missing_frames'] += 1
            if self.states['right']['missing_frames'] > self.timeout_frames:
                self.states['right']['data'] = None
    
    def get_left_gesture(self) -> Optional[dict]:
        """Get current left hand gesture."""
        return self.states['left']['data']
    
    def get_right_gesture(self) -> Optional[dict]:
        """Get current right hand gesture."""
        return self.states['right']['data']
    
    def reset(self):
        """Reset all states."""
        for hand in self.states:
            self.states[hand]['data'] = None
            self.states[hand]['missing_frames'] = 0


class GestureBuffer:
    """
    Buffers multiple frames of gesture data for consistency checking.
    
    Useful for filtering out single-frame noise.
    """
    
    def __init__(self, buffer_size: int = settings.SMOOTHING_WINDOW_SIZE):
        """Initialize gesture buffer."""
        self.buffer_size = buffer_size
        self.buffer = deque(maxlen=buffer_size)
    
    def add(self, gesture: str):
        """Add gesture to buffer."""
        self.buffer.append(gesture)
    
    def get_majority(self) -> Optional[str]:
        """
        Get most common gesture in buffer.
        
        Returns:
            str: Most frequent gesture or None if buffer empty
        """
        if not self.buffer:
            return None
        
        # Count occurrences
        counts = {}
        for g in self.buffer:
            counts[g] = counts.get(g, 0) + 1
        
        # Return most common
        return max(counts, key=counts.get) if counts else None
    
    def reset(self):
        """Clear buffer."""
        self.buffer.clear()
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        return len(self.buffer) == self.buffer_size
