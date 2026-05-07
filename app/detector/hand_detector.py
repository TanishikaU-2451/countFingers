"""
Hand detection using MediaPipe Hands.

This module provides real-time hand detection and landmark extraction
for up to 2 hands using MediaPipe's hand detection models.
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, List

from app.config import settings
from app.detector.landmarks import Landmark, Hand, HandsData
from app.utils.logger import logger


class HandDetector:
    """
    Detects hands and extracts landmarks using MediaPipe Hands.
    
    Handles:
    - Hand detection and tracking
    - Landmark extraction
    - Handedness classification (left/right with mirror correction)
    - Confidence filtering
    """
    
    def __init__(self):
        """Initialize MediaPipe hands detector."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=settings.MAX_HANDS,
            model_complexity=settings.MODEL_COMPLEXITY,
            min_detection_confidence=settings.HAND_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.HAND_TRACKING_CONFIDENCE,
        )
        
        self.frame_width = 0
        self.frame_height = 0
        
        logger.info(
            f"HandDetector initialized with max_hands={settings.MAX_HANDS}, "
            f"confidence={settings.HAND_DETECTION_CONFIDENCE}"
        )
    
    def detect(self, frame: np.ndarray) -> HandsData:
        """
        Detect hands in a frame.
        
        Args:
            frame: Input frame (BGR format from OpenCV)
        
        Returns:
            HandsData: Container with detected hands and landmarks
        """
        # Store frame dimensions for later use
        self.frame_height, self.frame_width = frame.shape[:2]
        
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame with MediaPipe
        results = self.hands.process(frame_rgb)
        
        # Container for detected hands
        hands_data = HandsData()
        
        # Extract detections
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness_info in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                # Extract landmarks
                landmarks = self._extract_landmarks(hand_landmarks)
                
                # Get handedness with mirror correction
                handedness = self._get_handedness(handedness_info)
                
                # Get confidence
                confidence = handedness_info.classification[0].score
                
                # Create Hand object
                hand = Hand(
                    handedness=handedness,
                    confidence=confidence,
                    landmarks=landmarks,
                    frame_width=self.frame_width,
                    frame_height=self.frame_height,
                )
                
                hands_data.add_hand(hand)
        
        return hands_data
    
    def _extract_landmarks(self, hand_landmarks) -> List[Landmark]:
        """
        Extract landmarks from MediaPipe results.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks object
        
        Returns:
            List: List of 21 Landmark objects
        """
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmark = Landmark(
                x=lm.x,
                y=lm.y,
                z=lm.z,
                visibility=lm.visibility,
            )
            landmarks.append(landmark)
        return landmarks
    
    def _get_handedness(self, handedness_info) -> str:
        """
        Get handedness with mirror correction for selfie images.
        
        MediaPipe assumes front-facing camera (selfie). For standard webcam
        with mirror effect, we apply a correction to get intuitive results.
        
        Args:
            handedness_info: MediaPipe handedness classification
        
        Returns:
            str: 'Left' or 'Right'
        """
        # Get the label from MediaPipe
        label = handedness_info.classification[0].label
        
        # Apply mirror correction for front-facing camera
        # Without correction: right hand shows as "Right" (MediaPipe is correct)
        # We invert it so it matches user perspective
        if settings.FLIP_FRAME_HORIZONTALLY:
            # Mirror correction: invert handedness
            return "Left" if label == "Right" else "Right"
        else:
            return label
    
    def close(self):
        """Close MediaPipe resources."""
        if self.hands:
            self.hands.close()
            logger.info("HandDetector closed")


class FrameProcessor:
    """
    Wrapper around hand detection for common preprocessing tasks.
    """
    
    def __init__(self, detector: HandDetector):
        """Initialize frame processor."""
        self.detector = detector
        self.frame_count = 0
        self.skip_count = 0
    
    def process_frame(self, frame: np.ndarray) -> tuple:
        """
        Process frame with optional skipping and corrections.
        
        Args:
            frame: Input frame (BGR)
        
        Returns:
            Tuple: (processed_frame, hands_data, should_detect)
        """
        self.frame_count += 1
        
        # Apply horizontal flip if configured
        if settings.FLIP_FRAME_HORIZONTALLY:
            frame = cv2.flip(frame, 1)
        
        # Determine if we should run detection
        should_detect = (self.skip_count % settings.FRAME_SKIP) == 0
        
        # Detect hands
        hands_data = self.detector.detect(frame) if should_detect else HandsData()
        
        self.skip_count += 1
        
        return frame, hands_data, should_detect
