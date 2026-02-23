"""
EasyOCR Text Extraction for Electrical Drawings
Extracts ALL text with coordinates before AI analysis
This solves the "Claude can't read small text" problem
"""

import easyocr
import cv2
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class ExtractedText:
    """Text detected by OCR with location and confidence"""
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    
    @property
    def center_x(self) -> int:
        return self.x + self.width // 2
    
    @property
    def center_y(self) -> int:
        return self.y + self.height // 2


class DrawingOCR:
    """
    Uses EasyOCR to extract ALL text from electrical drawings
    Provides coordinates so we can match text to equipment/lines
    """
    
    def __init__(self, languages=['en'], gpu=False):
        """
        Initialize EasyOCR reader
        
        Args:
            languages: List of languages to recognize (default: English only)
            gpu: Use GPU acceleration if available (default: False for compatibility)
        """
        console.print("[cyan]🔤 Initializing EasyOCR engine...[/cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading OCR models...", total=None)
            self.reader = easyocr.Reader(languages, gpu=gpu, verbose=False)
            progress.update(task, completed=True)
        console.print("[green]✓ OCR engine ready[/green]")
    
    def extract_text_from_image(self, image_path: str, 
                                min_confidence: float = 0.1) -> List[ExtractedText]:
        """
        Extract all text from drawing with coordinates
        
        TUNED: Lower confidence (0.1 vs 0.3) to catch small technical text
        
        Args:
            image_path: Path to drawing image
            min_confidence: Minimum confidence threshold (0-1) - LOWERED for technical drawings
        
        Returns:
            List of ExtractedText objects with coordinates
        """
        console.print(f"[cyan]📄 Extracting text from: {image_path}[/cyan]")
        
        # Read image
        image = cv2.imread(image_path)
        
        # Extract at multiple scales for better small text detection
        all_results = []
        
        # Original scale
        console.print("[cyan]  • Scanning at 100% scale...[/cyan]")
        results_1x = self._run_ocr(image)
        all_results.extend(results_1x)
        
        # 2x upscale for small text
        console.print("[cyan]  • Scanning at 200% scale (for small text)...[/cyan]")
        scaled_2x = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        results_2x = self._run_ocr(scaled_2x)
        # Adjust coordinates back to original scale
        for detection in results_2x:
            bbox, text, confidence = detection
            bbox = [[point[0]/2, point[1]/2] for point in bbox]
            all_results.append((bbox, text, confidence))
        
        # Deduplicate results (same text in same location from different scales)
        unique_results = self._deduplicate_results(all_results)
        
        # Parse results
        extracted_texts = []
        for detection in unique_results:
            bbox, text, confidence = detection
            
            if confidence >= min_confidence and len(text.strip()) > 0:
                # Get bounding box coordinates
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                x = int(min(x_coords))
                y = int(min(y_coords))
                width = int(max(x_coords) - min(x_coords))
                height = int(max(y_coords) - min(y_coords))
                
                extracted_texts.append(ExtractedText(
                    text=text.strip(),
                    x=x, y=y,
                    width=width,
                    height=height,
                    confidence=confidence
                ))
        
        console.print(f"[green]✓ Extracted {len(extracted_texts)} text regions[/green]")
        return extracted_texts
    
    def _run_ocr(self, image: np.ndarray) -> list:
        """Run EasyOCR on preprocessed image"""
        # Preprocess
        preprocessed = self._preprocess_for_ocr(image)
        
        # Run OCR with optimized settings for technical text
        results = self.reader.readtext(
            preprocessed,
            detail=1,
            paragraph=False,  # Don't merge text into paragraphs
            min_size=5,  # Detect very small text
            text_threshold=0.5,  # Lower threshold for technical text
            low_text=0.3,  # More aggressive text detection
            link_threshold=0.2,
            canvas_size=2800,  # Larger canvas for better small text
            mag_ratio=2.0  # Magnification for details
        )
        return results
    
    def _deduplicate_results(self, results: list) -> list:
        """Remove duplicate detections from multi-scale scanning"""
        unique = []
        seen = set()
        
        for bbox, text, conf in results:
            # Create key based on text and approximate location
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            center_x = int(sum(x_coords) / len(x_coords) / 10) * 10  # Round to nearest 10
            center_y = int(sum(y_coords) / len(y_coords) / 10) * 10
            
            key = (text.strip().lower(), center_x, center_y)
            
            if key not in seen:
                seen.add(key)
                unique.append((bbox, text, conf))
        
        return unique
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        
        Uses scikit-image for advanced preprocessing:
        - Denoising
        - Contrast enhancement
        - Sharpening
        """
        from skimage import exposure, filters
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Adaptive histogram equalization (improve contrast)
        enhanced = exposure.equalize_adapthist(denoised, clip_limit=0.03)
        enhanced = (enhanced * 255).astype(np.uint8)
        
        # Sharpen
        sharpened = filters.unsharp_mask(enhanced, radius=1, amount=1)
        sharpened = (sharpened * 255).astype(np.uint8)
        
        return sharpened
    
    def find_text_near_point(self, texts: List[ExtractedText], 
                            x: int, y: int, 
                            max_distance: int = 50) -> List[ExtractedText]:
        """
        Find text near a specific point (useful for finding specs near lines)
        
        Args:
            texts: List of extracted text
            x, y: Point coordinates
            max_distance: Maximum distance in pixels
        
        Returns:
            List of text objects near the point, sorted by distance
        """
        nearby = []
        for text in texts:
            # Calculate distance from point to text center
            distance = np.sqrt((text.center_x - x)**2 + (text.center_y - y)**2)
            if distance <= max_distance:
                nearby.append((distance, text))
        
        # Sort by distance (closest first)
        nearby.sort(key=lambda x: x[0])
        return [text for _, text in nearby]
    
    def find_text_in_box(self, texts: List[ExtractedText],
                        box_x: int, box_y: int,
                        box_width: int, box_height: int) -> List[ExtractedText]:
        """
        Find all text inside a bounding box (useful for reading equipment labels)
        
        Args:
            texts: List of extracted text
            box_x, box_y: Top-left corner of box
            box_width, box_height: Box dimensions
        
        Returns:
            List of text objects inside the box
        """
        inside = []
        for text in texts:
            # Check if text center is inside box
            if (box_x <= text.center_x <= box_x + box_width and
                box_y <= text.center_y <= box_y + box_height):
                inside.append(text)
        
        return inside
    
    def extract_wire_specifications(self, texts: List[ExtractedText]) -> Dict[str, List[str]]:
        """
        Parse extracted text to find electrical specifications
        
        Returns dict of:
        - wire_sizes: ["600 kcmil", "#1/0", "#12", etc.]
        - conduit_sizes: ["1-1/2 EMT", "2 RGS", etc.]
        - equipment_labels: ["SWITCHBOARD", "PP-1", etc.]
        """
        import re
        
        specs = {
            'wire_sizes': [],
            'conduit_sizes': [],
            'equipment_labels': [],
            'ground_wires': []
        }
        
        # Patterns for electrical specs
        wire_pattern = r'#?\d+/?[\d/]*\s*(AWG|kcmil|MCM)?'
        conduit_pattern = r'\d+[-/]?\d*["\s]*(EMT|RGS|IMC|PVC|RMC)'
        ground_pattern = r'#?\d+/?[\d/]*\s*(G|GND|GROUND)'
        equipment_pattern = r'(SWITCHBOARD|PANEL|PP-\d+|LP-\d+|RP-\d+|MSB|MDP)'
        
        for text_obj in texts:
            text = text_obj.text.upper()
            
            # Find wire sizes
            if re.search(wire_pattern, text, re.IGNORECASE):
                specs['wire_sizes'].append(text_obj.text)
            
            # Find conduit sizes
            if re.search(conduit_pattern, text, re.IGNORECASE):
                specs['conduit_sizes'].append(text_obj.text)
            
            # Find ground wires
            if re.search(ground_pattern, text, re.IGNORECASE):
                specs['ground_wires'].append(text_obj.text)
            
            # Find equipment labels
            if re.search(equipment_pattern, text, re.IGNORECASE):
                specs['equipment_labels'].append(text_obj.text)
        
        return specs
    
    def create_annotated_image(self, image_path: str, texts: List[ExtractedText],
                              output_path: str = "ocr_annotated.png"):
        """
        Create image showing detected text with bounding boxes
        Color-coded by confidence
        """
        image = cv2.imread(image_path)
        
        for text_obj in texts:
            # Color based on confidence
            if text_obj.confidence > 0.8:
                color = (0, 255, 0)  # Green = high confidence
            elif text_obj.confidence > 0.5:
                color = (0, 255, 255)  # Yellow = medium
            else:
                color = (0, 0, 255)  # Red = low confidence
            
            # Draw bounding box
            cv2.rectangle(image,
                         (text_obj.x, text_obj.y),
                         (text_obj.x + text_obj.width, text_obj.y + text_obj.height),
                         color, 2)
            
            # Add text label
            label = f"{text_obj.text} ({text_obj.confidence:.2f})"
            cv2.putText(image, label,
                       (text_obj.x, text_obj.y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        cv2.imwrite(output_path, image)
        console.print(f"[green]✓ Saved OCR visualization to: {output_path}[/green]")
        return output_path


def extract_text_from_drawing(image_path: str, min_confidence: float = 0.3) -> List[ExtractedText]:
    """
    Convenience function to extract text from a drawing
    
    Args:
        image_path: Path to drawing
        min_confidence: Minimum OCR confidence threshold
    
    Returns:
        List of ExtractedText objects
    """
    ocr = DrawingOCR()
    return ocr.extract_text_from_image(image_path, min_confidence)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ocr_extractor.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Extract text
    ocr = DrawingOCR()
    texts = ocr.extract_text_from_image(image_path)
    
    # Show results
    console.print("\n[bold cyan]📊 OCR EXTRACTION RESULTS:[/bold cyan]")
    console.print(f"Total text regions: {len(texts)}\n")
    
    # Parse specifications
    specs = ocr.extract_wire_specifications(texts)
    
    console.print("[bold]Wire Sizes Found:[/bold]")
    for wire in specs['wire_sizes'][:10]:  # Show first 10
        console.print(f"  • {wire}")
    
    console.print("\n[bold]Conduit Sizes Found:[/bold]")
    for conduit in specs['conduit_sizes'][:10]:
        console.print(f"  • {conduit}")
    
    console.print("\n[bold]Equipment Labels Found:[/bold]")
    for label in specs['equipment_labels'][:10]:
        console.print(f"  • {label}")
    
    # Create visualization
    ocr.create_annotated_image(image_path, texts)
