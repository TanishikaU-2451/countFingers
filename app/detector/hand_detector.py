"""
Hand detection using MediaPipe Hands (Tasks API v0.10+).

This module provides real-time hand detection and landmark extraction
for up to 2 hands using MediaPipe's hand detection models.
"""

import cv2
import numpy as np
from typing import Optional, List
import os
import time
import urllib.request
import tempfile
import shutil

from app.config import settings
from app.detector.landmarks import Landmark, Hand, HandsData
from app.utils.logger import logger

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision.core import image as mp_image
from mediapipe.tasks.python import vision as mp_vision


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
        """Initialize MediaPipe hands detector using Tasks API (v0.10+)."""
        self.frame_width = 0
        self.frame_height = 0
        self.hands = None
        self.enabled = True
        self._last_timestamp_ms = 0
        
        try:
            # Determine path to local model
            assets_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
            model_filename = 'hand_landmarker.task'
            model_path = os.path.abspath(os.path.join(assets_dir, model_filename))

            # If assets folder missing, create it
            os.makedirs(assets_dir, exist_ok=True)

            # If model not present, attempt to download it
            if not os.path.exists(model_path):
                logger.info(f"Model not found at {model_path}; attempting download...")
                try:
                    self._download_default_model(model_path)
                    logger.info(f"Downloaded hand_landmarker.task to {model_path}")
                except Exception as de:
                    logger.warning(f"Model download failed: {de}")

            # Build BaseOptions with model path if available, otherwise default
            if os.path.exists(model_path):
                base_options = python.BaseOptions(model_asset_path=model_path)
            else:
                base_options = python.BaseOptions()

            # Create hand landmarker options (use base_options)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=mp_vision.RunningMode.VIDEO,
                num_hands=settings.MAX_HANDS,
                min_hand_detection_confidence=settings.HAND_DETECTION_CONFIDENCE,
                min_hand_presence_confidence=settings.HAND_TRACKING_CONFIDENCE,
                min_tracking_confidence=settings.HAND_TRACKING_CONFIDENCE,
            )

            # Create the hand landmarker
            self.hands = vision.HandLandmarker.create_from_options(options)
            logger.info(
                f"HandDetector initialized with max_hands={settings.MAX_HANDS}, "
                f"confidence={settings.HAND_DETECTION_CONFIDENCE}"
            )
        except Exception as e:
            # If model file or bundled model is not available, disable detector
            logger.error(f"Failed to initialize HandDetector: {e}")
            logger.warning(
                "Hand detection disabled — provide a hand_landmarker.task model in assets/ "
                "or install a MediaPipe build that bundles models. Continuing without detection."
            )
            self.hands = None
            self.enabled = False

    def _download_default_model(self, destination_path: str):
        """Download a default hand_landmarker.task model to the given path.

        Uses the Google-hosted mediapipe assets bucket if reachable. This
        function uses urllib to avoid adding new dependencies.
        """
        # Official assets location (may change); fallback will raise on failure
        default_urls = [
            'https://storage.googleapis.com/mediapipe-assets/hand_landmarker.task',
            'https://storage.googleapis.com/mediapipe/hand_landmarker.task'
        ]

        last_err = None
        for url in default_urls:
            try:
                tmp_fd, tmp_path = tempfile.mkstemp(suffix='.task')
                os.close(tmp_fd)
                with urllib.request.urlopen(url, timeout=30) as resp, open(tmp_path, 'wb') as out:
                    shutil.copyfileobj(resp, out)
                # move into place
                os.replace(tmp_path, destination_path)
                return
            except Exception as e:
                last_err = e
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass

        raise RuntimeError(f"Failed to download model: {last_err}")
    
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
        # If detector not enabled, return empty result
        if not getattr(self, 'enabled', True) or self.hands is None:
            return HandsData()

        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaImage
        media_image = mp_image.Image(
            image_format=mp_image.ImageFormat.SRGB,
            data=frame_rgb
        )

        # MediaPipe video mode requires strictly increasing timestamps.
        timestamp_ms = int(time.monotonic() * 1000)
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        
        # Detect hands
        try:
            detection_result = self.hands.detect_for_video(media_image, timestamp_ms)
        except Exception as e:
            logger.warning(f"Detection error: {e}")
            return HandsData()
        
        # Container for detected hands
        hands_data = HandsData()
        
        # Extract detections
        if detection_result.hand_landmarks and detection_result.handedness:
            for index, hand_landmarks in enumerate(detection_result.hand_landmarks):
                handedness_info = None
                if index < len(detection_result.handedness):
                    handedness_entry = detection_result.handedness[index]
                    if isinstance(handedness_entry, list):
                        handedness_info = handedness_entry[0] if handedness_entry else None
                    else:
                        handedness_info = handedness_entry

                # Extract landmarks
                landmarks = []
                for lm in hand_landmarks:
                    landmark = Landmark(
                        x=lm.x,
                        y=lm.y,
                        z=lm.z,
                        visibility=getattr(lm, 'presence', 0.0),
                    )
                    landmarks.append(landmark)
                
                # Get handedness
                label = "Unknown"
                confidence = 0.0
                if handedness_info is not None:
                    label = getattr(handedness_info, 'category_name', None) or getattr(handedness_info, 'label', 'Unknown')
                    confidence = getattr(handedness_info, 'score', 0.0)

                # Apply mirror correction for front-facing camera
                if settings.FLIP_FRAME_HORIZONTALLY:
                    handedness = "Left" if label == "Right" else "Right"
                else:
                    handedness = label
                
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
    
    def close(self):
        """Close MediaPipe resources."""
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
