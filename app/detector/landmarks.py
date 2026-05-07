"""
Data classes and utilities for hand landmarks from MediaPipe.
"""

from dataclasses import dataclass
from typing import List, Tuple
from app.utils.geometry import get_bounding_box


@dataclass
class Landmark:
    """Represents a single hand landmark."""
    
    x: float  # Normalized x coordinate (0-1)
    y: float  # Normalized y coordinate (0-1)
    z: float  # Normalized z coordinate (depth)
    visibility: float  # Visibility confidence (0-1)
    
    def to_pixel(self, frame_width: int, frame_height: int) -> Tuple[int, int]:
        """Convert normalized coordinates to pixel coordinates."""
        return (int(self.x * frame_width), int(self.y * frame_height))
    
    def as_tuple(self) -> Tuple[float, float]:
        """Return (x, y) as tuple (normalized)."""
        return (self.x, self.y)
    
    def as_tuple_pixel(self, frame_width: int, frame_height: int) -> Tuple[int, int]:
        """Return (x, y) as pixel tuple."""
        return self.to_pixel(frame_width, frame_height)


@dataclass
class Hand:
    """Represents a detected hand with all landmarks."""
    
    handedness: str  # 'Left' or 'Right'
    confidence: float  # Detection confidence (0-1)
    landmarks: List[Landmark]  # 21 landmarks
    frame_width: int  # Frame width in pixels (for coordinate conversion)
    frame_height: int  # Frame height in pixels (for coordinate conversion)
    
    def get_landmark(self, index: int) -> Landmark:
        """
        Get landmark by index.
        
        Args:
            index: Landmark index (0-20)
        
        Returns:
            Landmark object
        """
        if 0 <= index < len(self.landmarks):
            return self.landmarks[index]
        return None
    
    def get_landmarks_pixel(self) -> List[Tuple[int, int]]:
        """Get all landmarks as pixel coordinates."""
        return [l.to_pixel(self.frame_width, self.frame_height) for l in self.landmarks]
    
    def get_landmarks_normalized(self) -> List[Tuple[float, float]]:
        """Get all landmarks as normalized coordinates."""
        return [l.as_tuple() for l in self.landmarks]
    
    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        """
        Get bounding box for this hand.
        
        Returns:
            Tuple: (x_min, y_min, x_max, y_max) in pixels
        """
        return get_bounding_box(self.get_landmarks_normalized(), self.frame_width, self.frame_height)
    
    def get_handedness_display(self) -> str:
        """Get display string for handedness."""
        return "Left" if self.handedness == "Left" else "Right"
    
    def is_visible(self, threshold: float = 0.5) -> bool:
        """
        Check if hand is adequately visible (average visibility above threshold).
        
        Args:
            threshold: Minimum average visibility (0-1)
        
        Returns:
            Bool: True if hand is visible
        """
        if not self.landmarks:
            return False
        avg_visibility = sum(l.visibility for l in self.landmarks) / len(self.landmarks)
        return avg_visibility >= threshold


class HandsData:
    """Container for detected hands in a frame."""
    
    def __init__(self):
        """Initialize empty hands data."""
        self.hands: List[Hand] = []
        self.timestamp: float = 0.0
    
    def add_hand(self, hand: Hand):
        """Add detected hand."""
        self.hands.append(hand)
    
    def get_left_hand(self) -> Hand:
        """Get left hand if detected."""
        for hand in self.hands:
            if hand.handedness == "Left":
                return hand
        return None
    
    def get_right_hand(self) -> Hand:
        """Get right hand if detected."""
        for hand in self.hands:
            if hand.handedness == "Right":
                return hand
        return None
    
    def get_hands_count(self) -> int:
        """Get number of detected hands."""
        return len(self.hands)
    
    def has_both_hands(self) -> bool:
        """Check if both hands are detected."""
        return self.get_left_hand() is not None and self.get_right_hand() is not None
    
    def get_all_hands(self) -> List[Hand]:
        """Get all detected hands."""
        return self.hands
    
    def clear(self):
        """Clear all hands data."""
        self.hands = []
