"""
Main frame renderer that combines all overlays and UI elements.

Orchestrates drawing of landmarks, text, performance metrics,
and gesture outputs on the frame.
"""

import cv2
import numpy as np
from typing import Optional, List

from app.config import settings
from app.detector.landmarks import Hand, HandsData
from app.ui.overlays import (
    LandmarkRenderer,
    BoundingBoxRenderer,
    TextRenderer,
    DebugRenderer
)
from app.utils.fps import FPSCounter
from app.utils.logger import logger


class FrameRenderer:
    """
    Main renderer for the application.
    
    Renders:
    - Hand landmarks and connections
    - Bounding boxes
    - Gesture outputs (finger counts)
    - Performance metrics (FPS, inference time)
    - Debug visualizations
    """
    
    def __init__(self):
        """Initialize frame renderer."""
        self.fps_counter = FPSCounter()
    
    def render_frame(
        self,
        frame: np.ndarray,
        hands_data: HandsData,
        gesture_results: dict,
        debug_mode: bool = settings.DEBUG_MODE
    ) -> None:
        """
        Render complete frame with all visualizations.
        
        This is the main rendering entry point.
        
        Args:
            frame: Frame to render on (modified in-place)
            hands_data: Detected hands
            gesture_results: Dict with 'left' and 'right' gesture data
            debug_mode: Enable debug visualizations
        """
        # Update FPS counter
        self.fps_counter.update()
        
        # Render each detected hand
        hands = hands_data.get_all_hands()
        for i, hand in enumerate(hands):
            self._render_hand(frame, hand, gesture_results, hand.handedness, debug_mode)
        
        # Render HUD with gesture outputs
        self._render_gesture_hud(frame, gesture_results)
        
        # Render performance metrics
        self._render_performance_hud(frame)
        
        # Render debug info if enabled
        if debug_mode and settings.DEBUG_MODE:
            self._render_debug_info(frame, hands_data)
    
    def _render_hand(
        self,
        frame: np.ndarray,
        hand: Hand,
        gesture_results: dict,
        handedness: str,
        debug_mode: bool
    ) -> None:
        """
        Render a single hand.
        
        Args:
            frame: Frame to render on
            hand: Hand object
            gesture_results: Gesture classification results
            handedness: 'Left' or 'Right'
            debug_mode: Enable debug rendering
        """
        # Choose colors based on handedness
        if handedness == 'Left':
            bbox_color = settings.BOUNDING_BOX_COLOR_LEFT
            gesture_key = 'left'
        else:
            bbox_color = settings.BOUNDING_BOX_COLOR_RIGHT
            gesture_key = 'right'
        
        # Render hand landmarks if debug enabled
        if debug_mode and settings.DEBUG_SHOW_LANDMARKS:
            LandmarkRenderer.draw_all_landmarks_and_connections(frame, hand)
        
        # Render bounding box
        if debug_mode and settings.DEBUG_SHOW_BOUNDING_BOX:
            BoundingBoxRenderer.draw_bounding_box(
                frame, hand, bbox_color,
                thickness=2,
                padding=10
            )
        
        # Render gesture label above hand
        gesture_data = gesture_results.get(gesture_key)
        if gesture_data and gesture_data.get('display'):
            label = gesture_data['display']
            x_min, y_min, _, _ = hand.get_bounding_box()
            TextRenderer.draw_text_with_background(
                frame,
                label,
                (max(0, x_min - 10), max(25, y_min - 20)),
                text_color=bbox_color,
                bg_color=settings.TEXT_BG_COLOR
            )
    
    def _render_gesture_hud(
        self,
        frame: np.ndarray,
        gesture_results: dict
    ) -> None:
        """
        Render gesture output HUD on left side of frame.
        
        Shows left and right hand finger counts or gestures.
        
        Args:
            frame: Frame to render on
            gesture_results: Gesture results dict
        """
        hud_lines = []
        
        # Add title
        hud_lines.append("=== Gesture Status ===")
        
        # Left hand
        left_gesture = gesture_results.get('left')
        if left_gesture and left_gesture.get('display'):
            hud_lines.append(left_gesture['display'])
        else:
            hud_lines.append("Left Hand: --")
        
        # Right hand
        right_gesture = gesture_results.get('right')
        if right_gesture and right_gesture.get('display'):
            hud_lines.append(right_gesture['display'])
        else:
            hud_lines.append("Right Hand: --")
        
        # Render HUD
        TextRenderer.draw_hud(
            frame,
            hud_lines,
            start_x=settings.STATUS_HUD_X_OFFSET,
            start_y=settings.STATUS_HUD_Y_START,
            line_spacing=settings.STATUS_HUD_LINE_SPACING,
        )
    
    def _render_performance_hud(self, frame: np.ndarray) -> None:
        """
        Render performance metrics HUD on right side of frame.
        
        Shows FPS and inference time.
        
        Args:
            frame: Frame to render on
        """
        perf_lines = [
            self.fps_counter.format_fps(),
            self.fps_counter.format_inference_time(),
        ]
        
        TextRenderer.draw_hud(
            frame,
            perf_lines,
            start_x=settings.PERF_HUD_X_OFFSET,
            start_y=settings.PERF_HUD_Y_START,
            line_spacing=settings.PERF_HUD_LINE_SPACING,
        )
    
    def _render_debug_info(
        self,
        frame: np.ndarray,
        hands_data: HandsData
    ) -> None:
        """
        Render additional debug information.
        
        Args:
            frame: Frame to render on
            hands_data: Detected hands
        """
        debug_lines = [
            f"Hands Detected: {hands_data.get_hands_count()}/{settings.MAX_HANDS}",
            f"Frame Size: {frame.shape[1]}x{frame.shape[0]}",
        ]
        
        # Render at bottom of frame
        TextRenderer.draw_hud(
            frame,
            debug_lines,
            start_x=settings.STATUS_HUD_X_OFFSET,
            start_y=frame.shape[0] - 100,
            line_spacing=settings.STATUS_HUD_LINE_SPACING,
        )
    
    def get_fps(self) -> float:
        """Get current FPS value."""
        return self.fps_counter.get_fps()
    
    def get_inference_time(self) -> float:
        """Get inference time in milliseconds."""
        return self.fps_counter.get_inference_time()


class RenderingPipeline:
    """
    Complete rendering pipeline orchestration.
    """
    
    def __init__(self):
        """Initialize rendering pipeline."""
        self.renderer = FrameRenderer()
        self.window_title = settings.WINDOW_TITLE
    
    def display_frame(self, frame: np.ndarray, key_handler=None) -> bool:
        """
        Display frame in OpenCV window and handle key input.
        
        Args:
            frame: Frame to display
            key_handler: Optional callback for key press handling
        
        Returns:
            Bool: False if window closed or Esc pressed
        """
        cv2.imshow(self.window_title, frame)
        
        # Wait for key press (1ms timeout)
        key = cv2.waitKey(1) & 0xFF
        
        # Check for exit key (Esc)
        if key == 27:
            return False
        
        # Handle other keys if callback provided
        if key_handler and key != 255:
            key_handler(key)
        
        # Return True to continue
        return True
    
    def close(self):
        """Close rendering windows."""
        cv2.destroyAllWindows()
    
    def get_fps(self) -> float:
        """Get current FPS."""
        return self.renderer.get_fps()
