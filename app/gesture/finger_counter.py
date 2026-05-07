"""
Finger counting and extension detection.

Implements angle-based finger extension detection to determine
how many fingers are raised on each hand.
"""

import math
from app.config import settings
from app.detector.landmarks import Hand
from app.utils.geometry import angle_between_points, distance
from app.utils.logger import logger


class FingerCounter:
    """
    Counts raised fingers on a hand using angle-based detection.
    
    Analyzes the angle at PIP joint to detect if each finger is extended.
    More robust than simple coordinate comparisons.
    """
    
    def __init__(self):
        """Initialize finger counter."""
        self.extension_threshold = settings.EXTENSION_ANGLE_THRESHOLD
        self.use_angles = settings.USE_ANGLE_BASED_DETECTION
    
    def count_fingers(self, hand: Hand) -> dict:
        """
        Count raised fingers on a hand.
        
        Returns dict with per-finger status and total count.
        
        Args:
            hand: Hand object with landmarks
        
        Returns:
            Dict with keys:
                'thumb': bool (extended)
                'index': bool (extended)
                'middle': bool (extended)
                'ring': bool (extended)
                'pinky': bool (extended)
                'total': int (total raised fingers)
                'angles': dict (angle values for each finger, for debugging)
        """
        result = {
            'thumb': False,
            'index': False,
            'middle': False,
            'ring': False,
            'pinky': False,
            'total': 0,
            'angles': {},
        }
        
        # Get landmarks in pixel coordinates for easier calculation
        landmarks_px = hand.get_landmarks_pixel()
        
        # Count each finger
        fingers_extended = []
        
        # Index finger (5, 6, 7, 8)
        index_extended = self._is_finger_extended(
            landmarks_px, 5, 6, 7, 8, "INDEX"
        )
        result['index'] = index_extended
        fingers_extended.append(index_extended)
        
        # Middle finger (9, 10, 11, 12)
        middle_extended = self._is_finger_extended(
            landmarks_px, 9, 10, 11, 12, "MIDDLE"
        )
        result['middle'] = middle_extended
        fingers_extended.append(middle_extended)
        
        # Ring finger (13, 14, 15, 16)
        ring_extended = self._is_finger_extended(
            landmarks_px, 13, 14, 15, 16, "RING"
        )
        result['ring'] = ring_extended
        fingers_extended.append(ring_extended)
        
        # Pinky finger (17, 18, 19, 20)
        pinky_extended = self._is_finger_extended(
            landmarks_px, 17, 18, 19, 20, "PINKY"
        )
        result['pinky'] = pinky_extended
        fingers_extended.append(pinky_extended)
        
        # Thumb (1, 2, 3, 4)
        # Special handling: thumb extends sideways, not up
        thumb_extended = self._is_thumb_extended(landmarks_px, hand)
        result['thumb'] = thumb_extended
        fingers_extended.append(thumb_extended)
        
        # Total count
        result['total'] = sum(fingers_extended)
        
        return result
    
    def _is_finger_extended(
        self,
        landmarks_px: list,
        mcp_idx: int,
        pip_idx: int,
        dip_idx: int,
        tip_idx: int,
        finger_name: str
    ) -> bool:
        """
        Detect if a finger is extended using angle-based method.
        
        A finger is considered extended if the angle at the PIP joint
        is greater than EXTENSION_ANGLE_THRESHOLD.
        
        Args:
            landmarks_px: Pixel coordinates of all landmarks
            mcp_idx: Metacarpophalangeal joint index
            pip_idx: Proximal interphalangeal joint index
            dip_idx: Distal interphalangeal joint index
            tip_idx: Finger tip index
            finger_name: Finger name for debugging
        
        Returns:
            Bool: True if finger is extended
        """
        try:
            if self.use_angles:
                # Angle-based detection
                # Calculate angle at PIP joint: MCP-PIP-DIP
                angle = angle_between_points(
                    landmarks_px[mcp_idx],
                    landmarks_px[pip_idx],
                    landmarks_px[dip_idx]
                )
                
                # Also check angle at DIP joint: PIP-DIP-TIP for confirmation
                angle_dip = angle_between_points(
                    landmarks_px[pip_idx],
                    landmarks_px[dip_idx],
                    landmarks_px[tip_idx]
                )
                
                # Finger is extended if both angles are large
                # (joints not bent)
                is_extended = (angle > self.extension_threshold and
                             angle_dip > self.extension_threshold)
                
                if settings.DEBUG_SHOW_ANGLES:
                    logger.debug(f"{finger_name}: PIP angle={angle:.1f}°, "
                               f"DIP angle={angle_dip:.1f}°, "
                               f"extended={is_extended}")
                
                return is_extended
            else:
                # Alternative: simple distance-based heuristic
                # Finger is extended if tip is further from base than middle joint
                dist_mcp_tip = distance(landmarks_px[mcp_idx], landmarks_px[tip_idx])
                dist_mcp_pip = distance(landmarks_px[mcp_idx], landmarks_px[pip_idx])
                
                return dist_mcp_tip > (dist_mcp_pip * settings.FINGER_RAISE_RATIO)
        
        except (IndexError, ValueError) as e:
            logger.warning(f"Error detecting {finger_name}: {e}")
            return False
    
    def _is_thumb_extended(self, landmarks_px: list, hand: Hand) -> bool:
        """
        Detect if thumb is extended.
        
        Thumb extends sideways (horizontally) rather than upward,
        so we use different logic than other fingers.
        
        Args:
            landmarks_px: Pixel coordinates of all landmarks
            hand: Hand object for handedness info
        
        Returns:
            Bool: True if thumb is extended
        """
        try:
            # Thumb joints: 1 (CMC), 2 (MCP), 3 (IP), 4 (TIP)
            # For thumb, we check if it extends away from hand center (wrist)
            
            # Calculate angle at IP joint: MCP-IP-TIP
            angle = angle_between_points(
                landmarks_px[2],  # MCP
                landmarks_px[3],  # IP
                landmarks_px[4]   # TIP
            )
            
            # Also check if thumb tip is far from other fingers
            # Thumb is abducted (away from hand)
            thumb_tip = landmarks_px[4]
            index_mcp = landmarks_px[5]
            
            thumb_index_distance = distance(thumb_tip, index_mcp)
            
            # Thumb is extended if angle is open and it's separated from index
            is_extended = (angle > self.extension_threshold and
                         thumb_index_distance > 30)  # Pixel threshold
            
            if settings.DEBUG_SHOW_ANGLES:
                logger.debug(f"THUMB: angle={angle:.1f}°, "
                           f"distance={thumb_index_distance:.1f}px, "
                           f"extended={is_extended}")
            
            return is_extended
        
        except (IndexError, ValueError) as e:
            logger.warning(f"Error detecting thumb: {e}")
            return False


class FingerCounterDebugger:
    """
    Debugging utilities for finger counting.
    """
    
    @staticmethod
    def format_finger_count(count_result: dict) -> str:
        """
        Format finger count result for display.
        
        Args:
            count_result: Result dict from count_fingers()
        
        Returns:
            str: Formatted display string
        """
        total = count_result['total']
        
        # Build detailed string
        details = []
        if count_result['thumb']:
            details.append("T")
        if count_result['index']:
            details.append("I")
        if count_result['middle']:
            details.append("M")
        if count_result['ring']:
            details.append("R")
        if count_result['pinky']:
            details.append("P")
        
        if details:
            return f"{total} ({', '.join(details)})"
        else:
            return str(total)
    
    @staticmethod
    def log_finger_analysis(hand_name: str, result: dict):
        """Log detailed finger analysis."""
        logger.debug(
            f"{hand_name}: "
            f"T={result['thumb']}, "
            f"I={result['index']}, "
            f"M={result['middle']}, "
            f"R={result['ring']}, "
            f"P={result['pinky']}, "
            f"Total={result['total']}"
        )
