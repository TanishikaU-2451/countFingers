"""
Gesture classification: detect fists, open hands, and other gestures.
"""

from app.config import settings
from app.gesture.finger_counter import FingerCounter
from app.detector.landmarks import Hand
from app.utils.logger import logger


class GestureClassifier:
    """
    Classifies hand gestures into categories.
    
    Current supports:
    - Open hand (fingers extended)
    - Fist (all fingers closed)
    """
    
    def __init__(self):
        """Initialize gesture classifier."""
        self.finger_counter = FingerCounter()
        self.fist_threshold = settings.FIST_THRESHOLD
    
    def classify(self, hand: Hand) -> dict:
        """
        Classify gesture for a hand.
        
        Args:
            hand: Hand object
        
        Returns:
            Dict with keys:
                'gesture': str ('open', 'fist', 'unknown')
                'finger_count': int (number of raised fingers)
                'confidence': float (gesture confidence 0-1)
                'details': dict (detailed finger states)
        """
        # Get finger count
        finger_details = self.finger_counter.count_fingers(hand)
        finger_count = finger_details['total']
        
        # Classify gesture
        gesture_type = self._classify_gesture(finger_count)
        
        # Calculate confidence based on finger consistency
        confidence = self._calculate_confidence(finger_details)
        
        return {
            'gesture': gesture_type,
            'finger_count': finger_count,
            'confidence': confidence,
            'details': finger_details,
        }
    
    def _classify_gesture(self, finger_count: int) -> str:
        """
        Classify gesture based on finger count.
        
        Args:
            finger_count: Number of raised fingers (0-5)
        
        Returns:
            str: Gesture type
        """
        if finger_count <= self.fist_threshold:
            return 'fist'
        elif finger_count >= 4:
            return 'open'
        else:
            return 'partial'
    
    def _calculate_confidence(self, finger_details: dict) -> float:
        """
        Calculate gesture confidence score.
        
        High confidence when all fingers agree clearly on state.
        
        Args:
            finger_details: Details from finger counting
        
        Returns:
            float: Confidence 0-1
        """
        # Simple heuristic: all fingers clearly distinct (all open or all closed)
        # gives high confidence
        
        finger_states = [
            finger_details['thumb'],
            finger_details['index'],
            finger_details['middle'],
            finger_details['ring'],
            finger_details['pinky'],
        ]
        
        # Count True vs False
        num_open = sum(finger_states)
        
        # High confidence if very few or very many fingers are open
        if num_open <= 1 or num_open >= 4:
            return 0.9
        else:
            # Medium confidence for partial states
            return 0.7
    
    def get_gesture_display(self, gesture: str, finger_count: int) -> str:
        """
        Get display string for gesture.
        
        Args:
            gesture: Gesture type from classify()
            finger_count: Finger count from classify()
        
        Returns:
            str: Display string
        """
        if gesture == 'fist':
            return f"Fist ({finger_count})"
        elif gesture == 'open':
            return str(finger_count)
        else:
            return str(finger_count)


class GestureRecognizer:
    """
    Full gesture recognition pipeline combining counting and classification.
    """
    
    def __init__(self):
        """Initialize gesture recognizer."""
        self.classifier = GestureClassifier()
    
    def recognize(self, hand: Hand) -> dict:
        """
        Recognize gesture for a hand.
        
        Args:
            hand: Hand object
        
        Returns:
            Dict with gesture info
        """
        result = self.classifier.classify(hand)
        return result
    
    def format_result(self, result: dict, handedness: str) -> str:
        """
        Format gesture result for display.
        
        Args:
            result: Result from recognize()
            handedness: 'Left' or 'Right'
        
        Returns:
            str: Display string like "Left Hand: 3" or "Right Hand: Fist (0)"
        """
        finger_count = result['finger_count']
        gesture = result['gesture']
        
        hand_label = f"{handedness} Hand"
        
        if gesture == 'fist':
            return f"{hand_label}: Fist ({finger_count})"
        else:
            return f"{hand_label}: {finger_count}"
