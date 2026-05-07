"""
Overlay rendering utilities for visual elements on frames.

Handles drawing landmarks, connections, bounding boxes, and text labels.
"""

import cv2
import numpy as np
from typing import Tuple, List

from app.config import settings
from app.detector.landmarks import Hand


class LandmarkRenderer:
    """Renders hand landmarks and connections."""
    
    @staticmethod
    def draw_landmarks(
        frame: np.ndarray,
        hand: Hand,
        radius: int = settings.LANDMARK_RADIUS,
        color: Tuple = settings.LANDMARK_COLOR,
        thickness: int = settings.LANDMARK_THICKNESS
    ) -> None:
        """
        Draw all landmarks on frame.
        
        Args:
            frame: Frame to draw on (modified in-place)
            hand: Hand object with landmarks
            radius: Circle radius in pixels
            color: Color in BGR format
            thickness: Circle thickness (-1 = filled)
        """
        landmarks_px = hand.get_landmarks_pixel()
        for i, (x, y) in enumerate(landmarks_px):
            cv2.circle(frame, (x, y), radius, color, thickness)
    
    @staticmethod
    def draw_connections(
        frame: np.ndarray,
        hand: Hand,
        connections: List[Tuple] = settings.HAND_CONNECTIONS,
        color: Tuple = settings.CONNECTION_COLOR,
        thickness: int = settings.CONNECTION_THICKNESS
    ) -> None:
        """
        Draw hand skeleton connections.
        
        Args:
            frame: Frame to draw on
            hand: Hand object
            connections: List of (start, end) landmark indices
            color: Color in BGR
            thickness: Line thickness
        """
        landmarks_px = hand.get_landmarks_pixel()
        
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks_px) and end_idx < len(landmarks_px):
                pt1 = landmarks_px[start_idx]
                pt2 = landmarks_px[end_idx]
                cv2.line(frame, pt1, pt2, color, thickness)
    
    @staticmethod
    def draw_fingertips(
        frame: np.ndarray,
        hand: Hand,
        radius: int = settings.FINGERTIP_RADIUS,
        color: Tuple = settings.FINGERTIP_COLOR,
        thickness: int = settings.FINGERTIP_THICKNESS
    ) -> None:
        """
        Draw highlighted fingertips.
        
        Args:
            frame: Frame to draw on
            hand: Hand object
            radius: Circle radius
            color: Color in BGR
            thickness: Circle thickness (-1 = filled)
        """
        # Fingertip indices
        fingertip_indices = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        landmarks_px = hand.get_landmarks_pixel()
        
        for idx in fingertip_indices:
            if idx < len(landmarks_px):
                x, y = landmarks_px[idx]
                cv2.circle(frame, (x, y), radius, color, thickness)
    
    @staticmethod
    def draw_all_landmarks_and_connections(
        frame: np.ndarray,
        hand: Hand
    ) -> None:
        """
        Draw complete hand visualization (landmarks, connections, fingertips).
        
        Args:
            frame: Frame to draw on
            hand: Hand object
        """
        LandmarkRenderer.draw_connections(frame, hand)
        LandmarkRenderer.draw_landmarks(frame, hand)
        LandmarkRenderer.draw_fingertips(frame, hand)


class BoundingBoxRenderer:
    """Renders bounding boxes for hands."""
    
    @staticmethod
    def draw_bounding_box(
        frame: np.ndarray,
        hand: Hand,
        color: Tuple,
        thickness: int = settings.BOUNDING_BOX_THICKNESS,
        padding: int = 10
    ) -> None:
        """
        Draw bounding box around hand.
        
        Args:
            frame: Frame to draw on
            hand: Hand object
            color: Color in BGR
            thickness: Box line thickness
            padding: Pixel padding around hand
        """
        x_min, y_min, x_max, y_max = hand.get_bounding_box()
        
        # Add padding
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(frame.shape[1], x_max + padding)
        y_max = min(frame.shape[0], y_max + padding)
        
        # Draw rectangle
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, thickness)
    
    @staticmethod
    def draw_bounding_box_with_label(
        frame: np.ndarray,
        hand: Hand,
        label: str,
        color: Tuple,
        thickness: int = settings.BOUNDING_BOX_THICKNESS,
        padding: int = 10
    ) -> None:
        """
        Draw bounding box with label text.
        
        Args:
            frame: Frame to draw on
            hand: Hand object
            label: Text to display above box
            color: Color in BGR
            thickness: Box thickness
            padding: Padding around hand
        """
        BoundingBoxRenderer.draw_bounding_box(frame, hand, color, thickness, padding)
        
        x_min, y_min, x_max, y_max = hand.get_bounding_box()
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        
        # Draw label above box
        label_y = max(25, y_min - 5)
        cv2.putText(
            frame,
            label,
            (x_min, label_y),
            settings.TEXT_FONT,
            settings.TEXT_FONT_SCALE,
            color,
            settings.TEXT_THICKNESS
        )


class TextRenderer:
    """Renders text labels and HUD information."""
    
    @staticmethod
    def draw_text(
        frame: np.ndarray,
        text: str,
        position: Tuple,
        color: Tuple = settings.TEXT_COLOR,
        font_scale: float = settings.TEXT_FONT_SCALE,
        thickness: int = settings.TEXT_THICKNESS,
        font: int = settings.TEXT_FONT
    ) -> None:
        """
        Draw text on frame.
        
        Args:
            frame: Frame to draw on
            text: Text to draw
            position: (x, y) coordinates
            color: Color in BGR
            font_scale: Font size scale
            thickness: Text thickness
            font: OpenCV font constant
        """
        cv2.putText(frame, text, position, font, font_scale, color, thickness)
    
    @staticmethod
    def draw_text_with_background(
        frame: np.ndarray,
        text: str,
        position: Tuple,
        text_color: Tuple = settings.TEXT_COLOR,
        bg_color: Tuple = settings.TEXT_BG_COLOR,
        font_scale: float = settings.TEXT_FONT_SCALE,
        thickness: int = settings.TEXT_THICKNESS,
        padding: int = 5
    ) -> None:
        """
        Draw text with semi-transparent background for better visibility.
        
        Args:
            frame: Frame to draw on
            text: Text to display
            position: (x, y) coordinates
            text_color: Text color in BGR
            bg_color: Background color in BGR
            font_scale: Font size scale
            thickness: Text thickness
            padding: Padding around text
        """
        x, y = position
        font = settings.TEXT_FONT
        
        # Get text size for background
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        # Expand box based on padding
        x1 = x - padding
        y1 = y - text_height - padding
        x2 = x + text_width + padding
        y2 = y + baseline + padding
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Draw text on top
        cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness)
    
    @staticmethod
    def draw_hud(
        frame: np.ndarray,
        lines: List[str],
        start_x: int = settings.STATUS_HUD_X_OFFSET,
        start_y: int = settings.STATUS_HUD_Y_START,
        line_spacing: int = settings.STATUS_HUD_LINE_SPACING,
        text_color: Tuple = settings.TEXT_COLOR,
        bg_color: Tuple = settings.TEXT_BG_COLOR
    ) -> None:
        """
        Draw HUD with multiple lines of text.
        
        Args:
            frame: Frame to draw on
            lines: List of text strings
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            line_spacing: Pixels between lines
            text_color: Text color
            bg_color: Background color
        """
        for i, line in enumerate(lines):
            y = start_y + (i * line_spacing)
            TextRenderer.draw_text_with_background(
                frame,
                line,
                (start_x, y),
                text_color=text_color,
                bg_color=bg_color
            )


class DebugRenderer:
    """Rendering utilities for debugging."""
    
    @staticmethod
    def draw_angle_indicators(
        frame: np.ndarray,
        hand: Hand,
        angle_values: dict,
           color: Tuple = settings.COLOR_YELLOW
    ) -> None:
        """
        Draw angle values at joints for debugging.
        
        Args:
            frame: Frame to draw on
            hand: Hand object
            angle_values: Dict with angle measurements
            color: Color for text
        """
        landmarks_px = hand.get_landmarks_pixel()
        
        # Draw angles at key joints
        text_color = (0, 255, 0) if settings.USE_ANGLE_BASED_DETECTION else (0, 0, 255)
        font_scale = 0.4
        thickness = 1
        
        # Sample positions for angle display
        key_points = [6, 10, 14, 18]  # PIP joints
        
        for i, pt_idx in enumerate(key_points):
            if pt_idx < len(landmarks_px):
                x, y = landmarks_px[pt_idx]
                if i < len(angle_values):
                    angle_text = f"{angle_values[i]:.0f}°"
                    cv2.putText(
                        frame, angle_text, (x, y),
                        settings.TEXT_FONT, font_scale,
                        text_color, thickness
                    )
