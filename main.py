"""
Real-time Hand Detection and Finger Counting Application

A production-style computer vision application that detects hands,
counts raised fingers, and identifies gestures like fists using:
- MediaPipe Hands for hand detection
- Angle-based finger extension detection
- Temporal smoothing for stability
- Real-time visualization with OpenCV

Usage:
    python main.py

Controls:
    ESC   - Exit application
    q     - Quit (alternative)

Author: Computer Vision Project
License: MIT
"""

import cv2
import sys
import time

from app.config import settings
from app.detector.hand_detector import HandDetector, FrameProcessor
from app.gesture.finger_counter import FingerCounter, FingerCounterDebugger
from app.gesture.gesture_classifier import GestureRecognizer
from app.gesture.smoothing import FingerCountSmoother, GestureStateTracker
from app.ui.renderer import RenderingPipeline
from app.utils.logger import logger
from app.utils.fps import FPSCounter


class HandDetectionApp:
    """
    Main application class orchestrating the complete pipeline.
    
    Pipeline:
    1. Capture frame from webcam
    2. Detect hands and extract landmarks
    3. Classify gestures and count fingers
    4. Apply temporal smoothing
    5. Render visualizations
    6. Display output
    """
    
    def __init__(self):
        """Initialize the application."""
        logger.info("Initializing Hand Detection Application...")
        
        # Initialize components
        self.hand_detector = HandDetector()
        self.frame_processor = FrameProcessor(self.hand_detector)
        self.gesture_recognizer = GestureRecognizer()
        
        # Smoothing for temporal stability
        self.left_finger_smoother = FingerCountSmoother()
        self.right_finger_smoother = FingerCountSmoother()
        self.gesture_tracker = GestureStateTracker()
        
        # Rendering
        self.rendering_pipeline = RenderingPipeline()
        
        # Camera initialization
        self.camera = None
        self.frame_width = settings.FRAME_WIDTH
        self.frame_height = settings.FRAME_HEIGHT
        
        logger.info("Application initialized successfully")
    
    def init_camera(self) -> bool:
        """
        Initialize camera capture.
        
        Returns:
            bool: True if successful
        """
        candidate_devices = []
        for device_index in [settings.CAMERA_DEVICE, 0, 1, 2, 3]:
            if device_index not in candidate_devices:
                candidate_devices.append(device_index)

        candidate_backends = [
            cv2.CAP_DSHOW,
            cv2.CAP_MSMF,
            0,
        ]

        for device_index in candidate_devices:
            for backend in candidate_backends:
                capture = None
                try:
                    capture = cv2.VideoCapture(device_index, backend) if backend else cv2.VideoCapture(device_index)
                    if not capture.isOpened():
                        if capture is not None:
                            capture.release()
                        continue

                    # Set camera properties
                    capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                    capture.set(cv2.CAP_PROP_FPS, settings.CAMERA_FPS)

                    # Set auto focus if supported
                    if settings.USE_AUTO_FOCUS:
                        try:
                            capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                        except Exception:
                            pass  # Not all cameras support this

                    # Warm up the camera with a couple of reads
                    frame = None
                    ret = False
                    for _ in range(2):
                        ret, frame = capture.read()
                        if ret:
                            break

                    if not ret or frame is None:
                        logger.warning(
                            f"Camera open failed on device {device_index} with backend {backend}; trying next option"
                        )
                        capture.release()
                        continue

                    # Success
                    self.camera = capture
                    self.frame_height, self.frame_width = frame.shape[:2]
                    logger.info(
                        f"Camera initialized: device={device_index}, backend={backend}, "
                        f"resolution={self.frame_width}x{self.frame_height}"
                    )
                    return True

                except Exception as e:
                    logger.warning(
                        f"Camera init failed on device {device_index} with backend {backend}: {e}"
                    )
                    if capture is not None:
                        capture.release()

        logger.error("Failed to initialize camera with all available device/backend combinations")
        return False
    
    def process_frame(self, frame) -> dict:
        """
        Process a single frame through the complete pipeline.
        
        Args:
            frame: Input frame from camera
        
        Returns:
            dict: Processing results
        """
        # Frame processing (preprocessing and hand detection)
        frame, hands_data, _ = self.frame_processor.process_frame(frame)
        
        # Gesture recognition
        gesture_results = self._recognize_gestures(hands_data)
        
        return {
            'frame': frame,
            'hands_data': hands_data,
            'gesture_results': gesture_results,
        }
    
    def _recognize_gestures(self, hands_data) -> dict:
        """
        Recognize gestures for detected hands with temporal smoothing.
        
        Args:
            hands_data: Detected hands
        
        Returns:
            dict: Gesture results for left and right hands
        """
        gesture_results = {
            'left': None,
            'right': None,
        }
        
        # Process left hand
        left_hand = hands_data.get_left_hand()
        if left_hand:
            result = self.gesture_recognizer.recognize(left_hand)
            finger_count = result['finger_count']
            
            # Apply temporal smoothing
            smoothed_count = self.left_finger_smoother.update(finger_count)
            
            # Update gesture tracker
            gesture_data = {
                'count': smoothed_count,
                'gesture': result['gesture'],
                'display': self.gesture_recognizer.format_result(
                    {'finger_count': smoothed_count, 'gesture': result['gesture']},
                    'Left'
                )
            }
            self.gesture_tracker.update_left(gesture_data)
            
            if settings.DEBUG_MODE:
                FingerCounterDebugger.log_finger_analysis("Left Hand", result['details'])
        else:
            # Hand disappeared
            self.gesture_tracker.update_left(None)
            self.left_finger_smoother.reset()
        
        # Process right hand
        right_hand = hands_data.get_right_hand()
        if right_hand:
            result = self.gesture_recognizer.recognize(right_hand)
            finger_count = result['finger_count']
            
            # Apply temporal smoothing
            smoothed_count = self.right_finger_smoother.update(finger_count)
            
            # Update gesture tracker
            gesture_data = {
                'count': smoothed_count,
                'gesture': result['gesture'],
                'display': self.gesture_recognizer.format_result(
                    {'finger_count': smoothed_count, 'gesture': result['gesture']},
                    'Right'
                )
            }
            self.gesture_tracker.update_right(gesture_data)
            
            if settings.DEBUG_MODE:
                FingerCounterDebugger.log_finger_analysis("Right Hand", result['details'])
        else:
            # Hand disappeared
            self.gesture_tracker.update_right(None)
            self.right_finger_smoother.reset()
        
        # Get stable gesture outputs
        gesture_results['left'] = self.gesture_tracker.get_left_gesture()
        gesture_results['right'] = self.gesture_tracker.get_right_gesture()
        
        return gesture_results
    
    def run(self) -> None:
        """
        Main application loop.
        
        Continuously:
        1. Capture frames
        2. Process hands and gestures
        3. Render visualizations
        4. Display output
        """
        # Initialize camera
        if not self.init_camera():
            logger.error("Failed to initialize camera. Exiting.")
            return
        
        logger.info("Starting main loop. Press ESC to exit")
        frame_count = 0
        
        try:
            while True:
                # Capture frame
                ret, frame = self.camera.read()
                
                if not ret:
                    logger.error("Failed to read from camera")
                    break
                
                frame_count += 1
                
                # Process frame
                result = self.process_frame(frame)
                processed_frame = result['frame']
                hands_data = result['hands_data']
                gesture_results = result['gesture_results']
                
                # Render frame
                self.rendering_pipeline.renderer.render_frame(
                    processed_frame,
                    hands_data,
                    gesture_results,
                    debug_mode=settings.DEBUG_MODE
                )
                
                # Display and handle input
                should_continue = self.rendering_pipeline.display_frame(processed_frame)
                if not should_continue:
                    break
                
                # Log periodically
                if frame_count % 100 == 0:
                    fps = self.rendering_pipeline.get_fps()
                    logger.info(
                        f"Frame {frame_count} | "
                        f"FPS: {fps:.1f} | "
                        f"Hands: {hands_data.get_hands_count()}"
                    )
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        
        if self.camera:
            self.camera.release()
        
        self.rendering_pipeline.close()
        self.hand_detector.close()
        
        logger.info("Application closed")


def main():
    """Entry point."""
    logger.info("=" * 60)
    logger.info("Hand Detection and Finger Counting Application")
    logger.info("=" * 60)
    
    # Create and run app
    app = HandDetectionApp()
    app.run()


if __name__ == "__main__":
    main()
