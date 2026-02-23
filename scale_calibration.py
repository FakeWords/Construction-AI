"""
Scale Calibration for Construction Drawings
Enables accurate distance measurements for material takeoffs
User calibrates like Bluebeam: draw line on known distance
"""

import numpy as np
from typing import Tuple, List

class DrawingScale:
    """Manages scale calibration and distance measurements"""
    
    def __init__(self):
        self.pixels_per_foot = None
        self.calibrated = False
    
    def calibrate(self, x1: int, y1: int, x2: int, y2: int, known_distance: float, unit: str = "feet"):
        """
        Calibrate scale using known distance
        
        Args:
            x1, y1: Start point of reference line (pixels)
            x2, y2: End point of reference line (pixels)
            known_distance: Actual distance this line represents
            unit: "feet", "meters", etc.
        """
        pixel_distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        if unit == "feet":
            self.pixels_per_foot = pixel_distance / known_distance
        elif unit == "meters":
            self.pixels_per_foot = pixel_distance / (known_distance * 3.28084)  # Convert to feet
        
        self.calibrated = True
        print(f"✓ Scale calibrated: {self.pixels_per_foot:.2f} pixels per foot")
    
    def measure_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Measure distance between two points in feet
        
        Returns: Distance in feet (or None if not calibrated)
        """
        if not self.calibrated:
            return None
        
        pixel_distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return pixel_distance / self.pixels_per_foot
    
    def measure_line_lengths(self, connection_lines: List) -> dict:
        """
        Measure all connection lines in drawing
        
        Returns: {line_index: distance_in_feet}
        """
        if not self.calibrated:
            return {}
        
        measurements = {}
        for idx, line in enumerate(connection_lines):
            distance = self.measure_distance(line.x1, line.y1, line.x2, line.y2)
            measurements[idx] = round(distance, 1)
        
        return measurements


# Example usage for web interface:
"""
// JavaScript for web UI
let calibrationMode = false;
let calibrationPoints = [];

function enableCalibration() {
    calibrationMode = true;
    alert("Click two points on the drawing at a known distance");
}

canvas.onclick = (e) => {
    if (calibrationMode) {
        calibrationPoints.push({x: e.offsetX, y: e.offsetY});
        
        if (calibrationPoints.length === 2) {
            let distance = prompt("What is the actual distance between these points (in feet)?");
            
            // Send to backend
            fetch('/api/calibrate', {
                method: 'POST',
                body: JSON.stringify({
                    x1: calibrationPoints[0].x,
                    y1: calibrationPoints[0].y,
                    x2: calibrationPoints[1].x,
                    y2: calibrationPoints[1].y,
                    known_distance: parseFloat(distance)
                })
            });
            
            calibrationMode = false;
            calibrationPoints = [];
        }
    }
};
"""
