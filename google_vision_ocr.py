"""
Google Cloud Vision OCR for Electrical Drawings
Production-grade text extraction with 95%+ accuracy
This is what professional construction tech companies use
"""

import os
import json
from google.cloud import vision
from google.oauth2 import service_account
import cv2
from typing import List, Dict, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class ExtractedText:
    """Text detected by Google Vision with location and confidence"""
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


class GoogleVisionOCR:
    """
    Google Cloud Vision API for OCR
    Best accuracy for technical drawings
    """
    
    def __init__(self, credentials_path: str = "google-vision-key.json"):
        """
        Initialize Google Vision client
        Reads credentials from GOOGLE_CREDENTIALS_JSON env var (production)
        or falls back to a local file (local development)
        """
        console.print("[cyan]☁️  Initializing Google Cloud Vision...[/cyan]")
        
        # Try environment variable first (production/Railway)
        credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        
        if credentials_json:
            # Load credentials from environment variable
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            console.print("[green]✓ Loaded credentials from environment variable[/green]")
        
        elif os.path.exists(credentials_path):
            # Fall back to local file (for local development)
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            console.print("[green]✓ Loaded credentials from local file[/green]")
        
        else:
            raise FileNotFoundError(
                f"Google Vision credentials not found.\n"
                f"Set the GOOGLE_CREDENTIALS_JSON environment variable, "
                f"or place a key file at: {credentials_path}"
            )
        
        # Create Vision API client
        self.client = vision.ImageAnnotatorClient(credentials=credentials)
        
        console.print("[green]✓ Google Vision ready[/green]")
    
    def extract_text_from_image(self, image_path: str) -> List[ExtractedText]:
        """
        Extract all text from drawing using Google Vision API
        
        Args:
            image_path: Path to drawing image
        
        Returns:
            List of ExtractedText objects with coordinates
        """
        console.print(f"[cyan]📄 Processing with Google Vision: {image_path}[/cyan]")
        
        # Read image
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # Call Google Vision API
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing drawing with Google Vision...", total=None)
            
            # Request DOCUMENT_TEXT_DETECTION (best for technical documents)
            response = self.client.document_text_detection(image=image)
            
            progress.update(task, completed=True)
        
        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")
        
        # Parse results
        extracted_texts = []
        
        # Get document-level text detection (better for technical docs)
        if response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        # Build paragraph text
                        para_text = ""
                        para_confidence = 0
                        
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            para_text += word_text + " "
                            para_confidence += word.confidence
                        
                        # Get bounding box
                        vertices = paragraph.bounding_box.vertices
                        x_coords = [v.x for v in vertices]
                        y_coords = [v.y for v in vertices]
                        
                        x = min(x_coords)
                        y = min(y_coords)
                        width = max(x_coords) - x
                        height = max(y_coords) - y
                        
                        avg_confidence = para_confidence / len(paragraph.words) if paragraph.words else 0
                        
                        if para_text.strip():
                            extracted_texts.append(ExtractedText(
                                text=para_text.strip(),
                                x=x, y=y,
                                width=width,
                                height=height,
                                confidence=avg_confidence
                            ))
        
        console.print(f"[green]✓ Extracted {len(extracted_texts)} text regions[/green]")
        return extracted_texts
    
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
            'ground_wires': [],
            'all_text': []
        }
        
        # Patterns for electrical specs
        wire_pattern = r'[\(]?\d+[\)]?\s*#?[\d/]+\s*(AWG|kcmil|KCMIL|MCM|kcm)?'
        conduit_pattern = r'\d+[-\s]?\d*/?\d*["\s]*(EMT|RGS|IMC|PVC|RMC|EMT\b)'
        ground_pattern = r'#?\d+/?[\d/]*\s*(G\b|GND|GROUND)'
        equipment_pattern = r'(SWITCHBOARD|SWBD|PANEL|PP-\d+|LP-\d+|RP-\d+|MSB|MDP|SB)'
        
        for text_obj in texts:
            text = text_obj.text
            specs['all_text'].append(text)
            
            # Find wire sizes
            wire_matches = re.findall(wire_pattern, text, re.IGNORECASE)
            if wire_matches:
                specs['wire_sizes'].append(text)
            
            # Find conduit sizes
            conduit_matches = re.findall(conduit_pattern, text, re.IGNORECASE)
            if conduit_matches:
                specs['conduit_sizes'].append(text)
            
            # Find ground wires
            ground_matches = re.findall(ground_pattern, text, re.IGNORECASE)
            if ground_matches:
                specs['ground_wires'].append(text)
            
            # Find equipment labels
            equipment_matches = re.findall(equipment_pattern, text, re.IGNORECASE)
            if equipment_matches:
                specs['equipment_labels'].append(text)
        
        return specs
    
    def create_annotated_image(self, image_path: str, texts: List[ExtractedText],
                              output_path: str = "google_vision_annotated.png"):
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
            
            # Add text label (truncate if too long)
            label = text_obj.text[:30] + "..." if len(text_obj.text) > 30 else text_obj.text
            cv2.putText(image, label,
                       (text_obj.x, text_obj.y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        cv2.imwrite(output_path, image)
        console.print(f"[green]✓ Saved Google Vision visualization to: {output_path}[/green]")
        return output_path


def extract_text_from_drawing(image_path: str, credentials_path: str = "google-vision-key.json") -> List[ExtractedText]:
    """
    Convenience function to extract text from a drawing using Google Vision
    
    Args:
        image_path: Path to drawing
        credentials_path: Path to Google Cloud credentials JSON
    
    Returns:
        List of ExtractedText objects
    """
    ocr = GoogleVisionOCR(credentials_path)
    return ocr.extract_text_from_image(image_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python google_vision_ocr.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Extract text
    ocr = GoogleVisionOCR()
    texts = ocr.extract_text_from_image(image_path)
    
    # Show results
    console.print("\n[bold cyan]📊 GOOGLE VISION OCR RESULTS:[/bold cyan]")
    console.print(f"Total text regions: {len(texts)}\n")
    
    # Parse specifications
    specs = ocr.extract_wire_specifications(texts)
    
    console.print("[bold]Wire Sizes Found:[/bold]")
    for wire in specs['wire_sizes'][:15]:  # Show first 15
        console.print(f"  • {wire}")
    
    console.print("\n[bold]Conduit Sizes Found:[/bold]")
    for conduit in specs['conduit_sizes'][:15]:
        console.print(f"  • {conduit}")
    
    console.print("\n[bold]Equipment Labels Found:[/bold]")
    for label in specs['equipment_labels'][:15]:
        console.print(f"  • {label}")
    
    console.print("\n[bold]Ground Wires Found:[/bold]")
    for gnd in specs['ground_wires'][:15]:
        console.print(f"  • {gnd}")
    
    # Create visualization
    ocr.create_annotated_image(image_path, texts)
    
    console.print(f"\n[bold green]Total unique text strings: {len(specs['all_text'])}[/bold green]")
