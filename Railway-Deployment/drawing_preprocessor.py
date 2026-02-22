"""
OpenCV Preprocessing for Electrical Drawings
Detects equipment boxes, connection lines, and text regions BEFORE AI analysis
This is what makes autonomous SLD reading possible
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class EquipmentBox:
    """Detected equipment box on drawing"""
    x: int
    y: int
    width: int
    height: int
    center_x: int
    center_y: int
    area: int
    has_text: bool = False
    
@dataclass  
class ConnectionLine:
    """Detected line connecting equipment"""
    x1: int
    y1: int
    x2: int
    y2: int
    length: float
    angle: float
    source_box: Optional[int] = None
    dest_box: Optional[int] = None
    text_region: Optional[Tuple[int, int, int, int]] = None

@dataclass
class TextRegion:
    """Detected text region (potential labels/specs)"""
    x: int
    y: int  
    width: int
    height: int
    near_line: Optional[int] = None
    near_box: Optional[int] = None


class DrawingPreprocessor:
    """
    Preprocesses electrical drawings to detect structure before AI analysis
    Uses OpenCV to find equipment boxes, connection lines, and text regions
    """
    
    def __init__(self, image_path: str):
        """Load and prepare image for analysis"""
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.height, self.width = self.gray.shape
        
        # Detection results
        self.equipment_boxes: List[EquipmentBox] = []
        self.connection_lines: List[ConnectionLine] = []
        self.text_regions: List[TextRegion] = []
        
    def detect_equipment_boxes(self, min_size: int = 5000, max_size: int = 100000) -> List[EquipmentBox]:
        """
        Detect rectangular equipment boxes (switchboards, panels, transformers)
        
        TUNED: Larger min_size to find WHOLE equipment, not internal compartments
        
        Returns equipment boxes sorted by size (largest first = likely main equipment)
        """
        # Adaptive threshold to handle varying contrast
        binary = cv2.adaptiveThreshold(
            self.gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Dilate to connect nearby components (merge buckets into whole switchboard)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        binary = cv2.dilate(binary, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        boxes = []
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Filter by size - LARGER min to get whole equipment
            if min_size < area < max_size:
                aspect_ratio = w / h if h > 0 else 0
                
                # Equipment boxes are roughly rectangular (not extreme aspect ratios)
                if 0.2 < aspect_ratio < 5.0:
                    boxes.append(EquipmentBox(
                        x=x, y=y, width=w, height=h,
                        center_x=x + w//2,
                        center_y=y + h//2,
                        area=area
                    ))
        
        # Sort by area (largest first - likely main equipment)
        boxes.sort(key=lambda b: b.area, reverse=True)
        
        self.equipment_boxes = boxes
        return boxes
    
    def detect_connection_lines(self, min_length: int = 100) -> List[ConnectionLine]:
        """
        Detect lines connecting equipment (electrical feeders)
        
        TUNED: Longer min_length to find MAJOR FEEDERS, not every tiny line
        
        Uses Hough Line Transform to find straight lines
        """
        # Edge detection
        edges = cv2.Canny(self.gray, 50, 150, apertureSize=3)
        
        # Detect lines using probabilistic Hough transform
        lines = cv2.HoughLinesP(
            edges, 
            rho=1, 
            theta=np.pi/180, 
            threshold=80,  # Higher threshold = fewer, stronger lines
            minLineLength=min_length,  # Longer minimum = major feeders only
            maxLineGap=20  # Larger gap tolerance
        )
        
        connection_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Calculate length and angle
                length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                
                # Only keep significant lines
                if length >= min_length:
                    # Filter out nearly horizontal/vertical lines that are likely borders
                    # Keep angled lines (likely actual connections)
                    angle_abs = abs(angle)
                    if not (85 < angle_abs < 95 or angle_abs < 5 or angle_abs > 175):
                        connection_lines.append(ConnectionLine(
                            x1=x1, y1=y1, x2=x2, y2=y2,
                            length=length,
                            angle=angle
                        ))
        
        self.connection_lines = connection_lines
        return connection_lines
    
    def detect_text_regions(self) -> List[TextRegion]:
        """
        Detect regions likely to contain text (labels, specs, annotations)
        
        Uses morphological operations to find text-like patterns
        """
        # Threshold
        _, binary = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphological operations to connect text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 3))
        dilated = cv2.dilate(binary, kernel, iterations=1)
        
        # Find text contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Text regions are typically wider than tall
            aspect_ratio = w / h if h > 0 else 0
            
            # Filter for text-like regions
            if aspect_ratio > 1.5 and 100 < w * h < 10000:
                text_regions.append(TextRegion(x=x, y=y, width=w, height=h))
        
        self.text_regions = text_regions
        return text_regions
    
    def associate_text_with_lines(self, proximity_threshold: int = 30):
        """
        Associate detected text regions with nearby connection lines
        Text near a line likely describes that feeder's specifications
        """
        for text_region in self.text_regions:
            text_center_x = text_region.x + text_region.width // 2
            text_center_y = text_region.y + text_region.height // 2
            
            min_distance = float('inf')
            nearest_line_idx = None
            
            for idx, line in enumerate(self.connection_lines):
                # Calculate distance from text center to line
                distance = self._point_to_line_distance(
                    text_center_x, text_center_y,
                    line.x1, line.y1, line.x2, line.y2
                )
                
                if distance < min_distance and distance < proximity_threshold:
                    min_distance = distance
                    nearest_line_idx = idx
            
            if nearest_line_idx is not None:
                text_region.near_line = nearest_line_idx
                # Store text region coordinates with the line
                self.connection_lines[nearest_line_idx].text_region = (
                    text_region.x, text_region.y, 
                    text_region.width, text_region.height
                )
    
    def associate_lines_with_boxes(self, proximity_threshold: int = 20):
        """
        Determine which equipment boxes each line connects
        This reveals the power distribution topology
        """
        for line_idx, line in enumerate(self.connection_lines):
            # Check line endpoints against box locations
            for box_idx, box in enumerate(self.equipment_boxes):
                # Check if line start point is near/in box
                if self._point_near_box(line.x1, line.y1, box, proximity_threshold):
                    if line.source_box is None:
                        line.source_box = box_idx
                
                # Check if line end point is near/in box  
                if self._point_near_box(line.x2, line.y2, box, proximity_threshold):
                    if line.dest_box is None:
                        line.dest_box = box_idx
    
    def _point_to_line_distance(self, px: int, py: int, 
                                  x1: int, y1: int, x2: int, y2: int) -> float:
        """Calculate perpendicular distance from point to line segment"""
        line_length_squared = (x2 - x1)**2 + (y2 - y1)**2
        
        if line_length_squared == 0:
            return np.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Calculate projection parameter
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length_squared))
        
        # Find closest point on line segment
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        # Return distance to closest point
        return np.sqrt((px - proj_x)**2 + (py - proj_y)**2)
    
    def _point_near_box(self, px: int, py: int, box: EquipmentBox, threshold: int) -> bool:
        """Check if point is near or inside equipment box"""
        # Check if point is inside box
        if (box.x <= px <= box.x + box.width and 
            box.y <= py <= box.y + box.height):
            return True
        
        # Check if point is near box edges
        if (box.x - threshold <= px <= box.x + box.width + threshold and
            box.y - threshold <= py <= box.y + box.height + threshold):
            return True
        
        return False
    
    def analyze_drawing_structure(self) -> Dict:
        """
        Complete analysis: detect all elements and their relationships
        
        Returns structured data about drawing topology
        """
        print("🔍 Preprocessing drawing with OpenCV...")
        
        # Detect all elements
        boxes = self.detect_equipment_boxes()
        print(f"   Found {len(boxes)} equipment boxes")
        
        lines = self.detect_connection_lines()
        print(f"   Found {len(lines)} connection lines")
        
        text_regions = self.detect_text_regions()
        print(f"   Found {len(text_regions)} text regions")
        
        # Associate elements
        self.associate_text_with_lines()
        self.associate_lines_with_boxes()
        
        # Build topology
        topology = {
            'equipment_boxes': boxes,
            'connection_lines': lines,
            'text_regions': text_regions,
            'main_equipment_idx': 0 if boxes else None,  # Largest box = likely main
        }
        
        # Identify likely main equipment (largest box with most connections)
        if boxes and lines:
            box_connections = [0] * len(boxes)
            for line in lines:
                if line.source_box is not None:
                    box_connections[line.source_box] += 1
                if line.dest_box is not None:
                    box_connections[line.dest_box] += 1
            
            # Main equipment = largest box with most connections
            main_idx = max(range(len(boxes)), 
                          key=lambda i: (box_connections[i], boxes[i].area))
            topology['main_equipment_idx'] = main_idx
        
        print(f"   ✓ Main equipment: Box #{topology.get('main_equipment_idx', 'unknown')}")
        
        return topology
    
    def create_annotated_image(self, output_path: str = None) -> np.ndarray:
        """
        Create annotated version of drawing showing detected elements
        Useful for debugging and visualization
        """
        annotated = self.image.copy()
        
        # Draw equipment boxes in blue
        for idx, box in enumerate(self.equipment_boxes):
            color = (255, 0, 0) if idx == 0 else (200, 200, 0)  # Main box in blue
            cv2.rectangle(annotated, 
                         (box.x, box.y), 
                         (box.x + box.width, box.y + box.height),
                         color, 2)
            cv2.putText(annotated, f"Box {idx}", 
                       (box.x, box.y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Draw connection lines in green
        for idx, line in enumerate(self.connection_lines):
            cv2.line(annotated, (line.x1, line.y1), (line.x2, line.y2), (0, 255, 0), 2)
            
            # Mark text regions on lines in red
            if line.text_region:
                tx, ty, tw, th = line.text_region
                cv2.rectangle(annotated, (tx, ty), (tx + tw, ty + th), (0, 0, 255), 1)
        
        if output_path:
            cv2.imwrite(output_path, annotated)
        
        return annotated


def preprocess_electrical_drawing(image_path: str) -> Dict:
    """
    Convenience function to preprocess an electrical drawing
    
    Returns topology data ready for AI analysis
    """
    preprocessor = DrawingPreprocessor(image_path)
    return preprocessor.analyze_drawing_structure()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python drawing_preprocessor.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Analyze structure
    topology = preprocess_electrical_drawing(image_path)
    
    print(f"\n📊 PREPROCESSING RESULTS:")
    print(f"   Equipment boxes: {len(topology['equipment_boxes'])}")
    print(f"   Connection lines: {len(topology['connection_lines'])}")
    print(f"   Text regions: {len(topology['text_regions'])}")
    print(f"   Main equipment: Box #{topology.get('main_equipment_idx', 'unknown')}")
    
    # Create annotated image
    preprocessor = DrawingPreprocessor(image_path)
    preprocessor.analyze_drawing_structure()
    annotated = preprocessor.create_annotated_image("annotated_drawing.png")
    print(f"\n✓ Saved annotated image to: annotated_drawing.png")
