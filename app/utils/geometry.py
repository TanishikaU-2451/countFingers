"""
Geometry utilities for hand landmark calculations and angle detection.
"""

import math
import numpy as np


def distance(point1, point2):
    """
    Calculate Euclidean distance between two 2D points.
    
    Args:
        point1: Tuple or array-like (x1, y1)
        point2: Tuple or array-like (x2, y2)
    
    Returns:
        Float: Euclidean distance
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def distance_3d(point1, point2):
    """
    Calculate Euclidean distance between two 3D points.
    
    Args:
        point1: Tuple or array-like (x1, y1, z1)
        point2: Tuple or array-like (x2, y2, z2)
    
    Returns:
        Float: Euclidean distance
    """
    return math.sqrt(
        (point1[0] - point2[0]) ** 2 +
        (point1[1] - point2[1]) ** 2 +
        (point1[2] - point2[2]) ** 2
    )


def angle_between_points(point_a, point_b, point_c):
    """
    Calculate angle at point_b formed by points A-B-C (in degrees).
    
    This uses the dot product formula: angle = arccos(dot_product / (magnitude1 * magnitude2))
    
    Args:
        point_a: First point (x, y)
        point_b: Vertex point where angle is calculated (x, y)
        point_c: Third point (x, y)
    
    Returns:
        Float: Angle in degrees (0-180)
    """
    # Vector from B to A
    vector_ba = (point_a[0] - point_b[0], point_a[1] - point_b[1])
    
    # Vector from B to C
    vector_bc = (point_c[0] - point_b[0], point_c[1] - point_b[1])
    
    # Calculate magnitudes
    magnitude_ba = math.sqrt(vector_ba[0] ** 2 + vector_ba[1] ** 2)
    magnitude_bc = math.sqrt(vector_bc[0] ** 2 + vector_bc[1] ** 2)
    
    # Avoid division by zero
    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0
    
    # Calculate dot product
    dot_product = vector_ba[0] * vector_bc[0] + vector_ba[1] * vector_bc[1]
    
    # Calculate cosine of angle
    cos_angle = dot_product / (magnitude_ba * magnitude_bc)
    
    # Clamp to [-1, 1] to avoid numerical errors with arccos
    cos_angle = max(-1, min(1, cos_angle))
    
    # Calculate angle in radians and convert to degrees
    angle_radians = math.acos(cos_angle)
    angle_degrees = math.degrees(angle_radians)
    
    return angle_degrees


def angle_between_points_3d(point_a, point_b, point_c):
    """
    Calculate angle at point_b formed by points A-B-C in 3D space (in degrees).
    
    Args:
        point_a: First point (x, y, z)
        point_b: Vertex point where angle is calculated (x, y, z)
        point_c: Third point (x, y, z)
    
    Returns:
        Float: Angle in degrees (0-180)
    """
    # Vector from B to A
    vector_ba = np.array([
        point_a[0] - point_b[0],
        point_a[1] - point_b[1],
        point_a[2] - point_b[2]
    ])
    
    # Vector from B to C
    vector_bc = np.array([
        point_c[0] - point_b[0],
        point_c[1] - point_b[1],
        point_c[2] - point_b[2]
    ])
    
    # Calculate magnitudes
    magnitude_ba = np.linalg.norm(vector_ba)
    magnitude_bc = np.linalg.norm(vector_bc)
    
    # Avoid division by zero
    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0
    
    # Calculate cosine of angle using dot product
    cos_angle = np.dot(vector_ba, vector_bc) / (magnitude_ba * magnitude_bc)
    
    # Clamp to [-1, 1] to avoid numerical errors
    cos_angle = max(-1, min(1, cos_angle))
    
    # Calculate angle in radians and convert to degrees
    angle_radians = math.acos(cos_angle)
    angle_degrees = math.degrees(angle_radians)
    
    return angle_degrees


def get_bounding_box(landmarks, frame_width, frame_height):
    """
    Calculate bounding box for landmarks.
    
    Args:
        landmarks: List of (x, y) normalized landmarks (0-1 range)
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
    
    Returns:
        Tuple: (x_min, y_min, x_max, y_max) in pixel coordinates
    """
    if not landmarks:
        return None
    
    # Convert normalized coordinates to pixel coordinates
    x_coords = [l[0] * frame_width for l in landmarks]
    y_coords = [l[1] * frame_height for l in landmarks]
    
    x_min = int(min(x_coords))
    x_max = int(max(x_coords))
    y_min = int(min(y_coords))
    y_max = int(max(y_coords))
    
    return (x_min, y_min, x_max, y_max)


def point_in_bbox(point, bbox):
    """
    Check if a point is inside a bounding box.
    
    Args:
        point: Tuple (x, y)
        bbox: Tuple (x_min, y_min, x_max, y_max)
    
    Returns:
        Bool: True if point is inside bbox
    """
    x, y = point
    x_min, y_min, x_max, y_max = bbox
    return x_min <= x <= x_max and y_min <= y <= y_max


def normalize_landmarks(landmarks, frame_width, frame_height):
    """
    Normalize landmark coordinates to 0-1 range.
    
    Args:
        landmarks: List of pixel coordinates (x, y)
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
    
    Returns:
        List: Normalized coordinates (0-1 range)
    """
    return [(x / frame_width, y / frame_height) for x, y in landmarks]


def denormalize_landmarks(landmarks, frame_width, frame_height):
    """
    Convert normalized coordinates to pixel coordinates.
    
    Args:
        landmarks: List of normalized coordinates (x, y) in 0-1 range
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
    
    Returns:
        List: Pixel coordinates (x, y)
    """
    return [(int(x * frame_width), int(y * frame_height)) for x, y in landmarks]
