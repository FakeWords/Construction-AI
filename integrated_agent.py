"""
FIELDWISE AI - ULTIMATE DRAWING ANALYZER
Combines OpenCV (structure) + Google Vision (OCR) + Claude (reasoning)
This is production-grade automated electrical takeoff
"""

import anthropic
import base64
import json
from PIL import Image
import io
from typing import Dict, List, Optional, Tuple
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import our preprocessing modules
from drawing_preprocessor import DrawingPreprocessor, EquipmentBox, ConnectionLine
from google_vision_ocr import GoogleVisionOCR, ExtractedText
from text_assembly import assemble_drawing_text, SmartTextAssembler, TextBlock

# Import electrical equipment logic
from switchboard_logic import (
    SWITCHBOARD_LOGIC,
    MAIN_TIE_MAIN_LOGIC,
    SERVICE_ENTRANCE_LOGIC,
    PARALLEL_CONDUCTORS_LOGIC,
    CIRCUIT_BREAKER_NOTATION,
    WIRE_SIZING_VALIDATION,
    INTEGRATION_RULES
)
from electrical_equipment_complete import (
    TRANSFORMER_LOGIC,
    SUBSTATION_LOGIC,
    PANEL_TYPES_LOGIC,
    SWITCHGEAR_LOGIC,
    AUTOMATIC_TRANSFER_SWITCH_LOGIC,
    GENERATOR_LOGIC,
    BUS_DUCT_LOGIC,
    MOTOR_CONTROL_CENTER_LOGIC
)
from multitrade_equipment_logic import (
    HVAC_EQUIPMENT_LOGIC,
    ROOFTOP_UNIT_LOGIC,
    CHILLER_LOGIC,
    BOILER_LOGIC,
    DUCTWORK_SIZING_LOGIC,
    VAV_SYSTEM_LOGIC,
    PLUMBING_SYSTEM_LOGIC,
    DRAIN_SYSTEM_LOGIC,
    WATER_HEATER_LOGIC,
    FIRE_SPRINKLER_LOGIC,
    FIRE_PUMP_LOGIC,
    FIRE_ALARM_SYSTEM_LOGIC
)

# Import trade knowledge
from trade_knowledge import (
    validate_electrical_circuit,
    validate_hvac_duct,
    validate_plumbing_pipe,
    validate_fire_sprinkler,
)

console = Console()

# API Configuration
API_KEY = "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"
client = anthropic.Anthropic(api_key=API_KEY)


class IntegratedDrawingAgent:
    """
    The ultimate drawing analyzer combining:
    - OpenCV for structure detection
    - Google Vision for OCR
    - Claude for reasoning and validation
    """
    
    def __init__(self, image_path: str, trade: str = "electrical"):
        self.image_path = image_path
        self.trade = trade
        
        console.print(Panel.fit(
            f"[bold cyan]FIELDWISE AI - INTEGRATED ANALYZER[/bold cyan]\n"
            f"Drawing: {image_path}\n"
            f"Trade: {trade.upper()}",
            border_style="cyan"
        ))
        
        # Phase 1: OpenCV Structure Detection
        console.print("\n[bold yellow]═══ PHASE 1: STRUCTURE DETECTION (OpenCV) ═══[/bold yellow]")
        preprocessor = DrawingPreprocessor(image_path)
        self.structure = preprocessor.analyze_drawing_structure()
        
        self.equipment_boxes = self.structure['equipment_boxes']
        self.connection_lines = self.structure['connection_lines']
        
        # Phase 2: Google Vision OCR
        console.print("\n[bold yellow]═══ PHASE 2: TEXT EXTRACTION (Google Vision) ═══[/bold yellow]")
        ocr = GoogleVisionOCR()
        self.all_text = ocr.extract_text_from_image(image_path)
        
        # Phase 2.5: Smart Text Assembly
        console.print("\n[bold yellow]═══ PHASE 2.5: SMART TEXT ASSEMBLY ═══[/bold yellow]")
        assembler = SmartTextAssembler()
        self.assembled_blocks = assembler.assemble_text_blocks(self.all_text)
        
        console.print(f"[green]✓ Assembled {len(self.assembled_blocks)} logical text blocks[/green]")
        console.print(f"[green]  (Regex parsing removed - Claude will interpret variations)[/green]")
        
        # Phase 3: Match Text to Structure
        console.print("\n[bold yellow]═══ PHASE 3: MATCHING TEXT TO STRUCTURE ═══[/bold yellow]")
        self.matched_data = self._match_text_to_structure()
        
        console.print(f"[green]✓ Matched {len(self.matched_data['equipment_with_labels'])} equipment boxes with labels[/green]")
        console.print(f"[green]✓ Matched {len(self.matched_data['lines_with_specs'])} connection lines with specs[/green]")
    
    def _match_text_to_structure(self) -> Dict:
        """
        Match extracted text to detected structure
        
        Returns:
            equipment_with_labels: Equipment boxes with their text labels
            lines_with_specs: Connection lines with their wire specifications
        """
        matched = {
            'equipment_with_labels': [],
            'lines_with_specs': [],
            'unmatched_text': []
        }
        
        # Match text to equipment boxes
        for idx, box in enumerate(self.equipment_boxes):
            texts_in_box = []
            for text_obj in self.all_text:
                # Check if text center is inside box
                if (box.x <= text_obj.center_x <= box.x + box.width and
                    box.y <= text_obj.center_y <= box.y + box.height):
                    texts_in_box.append(text_obj.text)
            
            matched['equipment_with_labels'].append({
                'box_index': idx,
                'location': (box.x, box.y),
                'size': (box.width, box.height),
                'labels': texts_in_box,
                'is_main': idx == self.structure.get('main_equipment_idx')
            })
        
        # Match text to connection lines
        for idx, line in enumerate(self.connection_lines):
            texts_near_line = []
            
            # Find text within 50 pixels of line
            for text_obj in self.all_text:
                dist = self._point_to_line_distance(
                    text_obj.center_x, text_obj.center_y,
                    line.x1, line.y1, line.x2, line.y2
                )
                if dist < 50:
                    texts_near_line.append(text_obj.text)
            
            if texts_near_line:
                matched['lines_with_specs'].append({
                    'line_index': idx,
                    'from': (line.x1, line.y1),
                    'to': (line.x2, line.y2),
                    'source_box': line.source_box,
                    'dest_box': line.dest_box,
                    'specs': texts_near_line
                })
        
        return matched
    
    def _point_to_line_distance(self, px: int, py: int, 
                                  x1: int, y1: int, x2: int, y2: int) -> float:
        """Calculate perpendicular distance from point to line segment"""
        line_length_squared = (x2 - x1)**2 + (y2 - y1)**2
        
        if line_length_squared == 0:
            return np.sqrt((px - x1)**2 + (py - y1)**2)
        
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length_squared))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return np.sqrt((px - proj_x)**2 + (py - proj_y)**2)
    
    def analyze(self) -> str:
        """
        Run Claude analysis with pre-extracted structure and text
        Claude doesn't need to struggle reading - we give it everything
        """
        console.print("\n[bold yellow]═══ PHASE 4: CLAUDE ANALYSIS & VALIDATION ═══[/bold yellow]")
        
        # Build comprehensive prompt with all extracted data
        analysis_prompt = self._build_analysis_prompt()
        
        # Call Claude for reasoning and validation
        console.print("[cyan]🤖 Claude is analyzing the pre-extracted data...[/cyan]")
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": analysis_prompt
            }]
        )
        
        analysis = response.content[0].text
        
        console.print("[green]✓ Analysis complete[/green]")
        return analysis
    
    def _build_analysis_prompt(self) -> str:
        """Build comprehensive prompt with all pre-extracted data"""
        
        # Select knowledge base based on trade
        if self.trade == "electrical":
            equipment_knowledge = f"""
═══════════════════════════════════════════════════════════════
ELECTRICAL EQUIPMENT KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════

{SWITCHBOARD_LOGIC}

{CIRCUIT_BREAKER_NOTATION}

{TRANSFORMER_LOGIC}

{SUBSTATION_LOGIC}

{PANEL_TYPES_LOGIC}

{SWITCHGEAR_LOGIC}

{AUTOMATIC_TRANSFER_SWITCH_LOGIC}

{GENERATOR_LOGIC}

{BUS_DUCT_LOGIC}

{MOTOR_CONTROL_CENTER_LOGIC}

{PARALLEL_CONDUCTORS_LOGIC}

{SERVICE_ENTRANCE_LOGIC}

{MAIN_TIE_MAIN_LOGIC}

{WIRE_SIZING_VALIDATION}

{INTEGRATION_RULES}
"""
        elif self.trade == "mechanical" or self.trade == "hvac":
            equipment_knowledge = f"""
═══════════════════════════════════════════════════════════════
HVAC/MECHANICAL EQUIPMENT KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════

{HVAC_EQUIPMENT_LOGIC}

{ROOFTOP_UNIT_LOGIC}

{CHILLER_LOGIC}

{BOILER_LOGIC}

{DUCTWORK_SIZING_LOGIC}

{VAV_SYSTEM_LOGIC}
"""
        elif self.trade == "plumbing":
            equipment_knowledge = f"""
═══════════════════════════════════════════════════════════════
PLUMBING EQUIPMENT KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════

{PLUMBING_SYSTEM_LOGIC}

{DRAIN_SYSTEM_LOGIC}

{WATER_HEATER_LOGIC}
"""
        elif self.trade == "fire_protection":
            equipment_knowledge = f"""
═══════════════════════════════════════════════════════════════
FIRE PROTECTION EQUIPMENT KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════

{FIRE_SPRINKLER_LOGIC}

{FIRE_PUMP_LOGIC}

{FIRE_ALARM_SYSTEM_LOGIC}
"""
        else:
            equipment_knowledge = "General construction drawing analysis."
        
        prompt = f"""You are a professional {self.trade} engineer with 20+ years experience analyzing construction drawings.

I've already extracted ALL the information from the drawing using computer vision and OCR.
Your job is to INTERPRET this data, VALIDATE it, and create a professional analysis.

{equipment_knowledge}

═══════════════════════════════════════════════════════════════
EQUIPMENT DETECTED ({len(self.matched_data['equipment_with_labels'])} boxes):
═══════════════════════════════════════════════════════════════
"""
        
        # Add equipment data
        for equip in self.matched_data['equipment_with_labels']:
            is_main = " ← LIKELY MAIN EQUIPMENT" if equip['is_main'] else ""
            prompt += f"\nEquipment Box #{equip['box_index']}{is_main}:\n"
            prompt += f"  Location: ({equip['location'][0]}, {equip['location'][1]})\n"
            prompt += f"  Size: {equip['size'][0]}x{equip['size'][1]} pixels\n"
            prompt += f"  Text found inside:\n"
            for label in equip['labels']:
                prompt += f"    • {label}\n"
        
        prompt += f"""
═══════════════════════════════════════════════════════════════
CONNECTION LINES DETECTED ({len(self.matched_data['lines_with_specs'])} feeders):
═══════════════════════════════════════════════════════════════
"""
        
        # Add connection line data
        for conn in self.matched_data['lines_with_specs']:
            prompt += f"\nConnection #{conn['line_index']}:\n"
            if conn['source_box'] is not None and conn['dest_box'] is not None:
                prompt += f"  Connects: Box #{conn['source_box']} → Box #{conn['dest_box']}\n"
            prompt += f"  Specifications found on this line:\n"
            for spec in conn['specs']:
                prompt += f"    • {spec}\n"
        
        prompt += f"""
═══════════════════════════════════════════════════════════════
ASSEMBLED TEXT BLOCKS ({len(self.assembled_blocks)} blocks):
═══════════════════════════════════════════════════════════════

These text blocks have been intelligently grouped from fragmented OCR.
Your job: PARSE these blocks to extract equipment specifications.

The format will vary by drawing. Common patterns include:
- "225AF / 110AT" (spaced format)
- "LSI125AT150AS225AF" (concatenated format)
- Table rows with separated values
- Any other variation

YOU must identify the pattern and extract:
- Frame ratings (AF)
- Trip ratings (AT/AS/AE)
- Wire sizes (kcmil, AWG)
- Panel labels (PP-1, LP-2, etc.)
- Equipment ratings

ASSEMBLED BLOCKS:
"""
        
        for i, block in enumerate(self.assembled_blocks):
            prompt += f"Block {i}: \"{block.combined_text}\"\n"
        
        prompt += """
═══════════════════════════════════════════════════════════════
PARSING INSTRUCTIONS:
═══════════════════════════════════════════════════════════════

LOOK FOR PATTERNS in the blocks above:

**SWITCHBOARD BUCKETS:**
Could be formatted as:
- "225AF / 110AT" → Frame=225, Trip=110
- "LSI125AT150AS225AF" → Protection=LSI, Trip=125AT, Frame=225AF
- "Bucket 3: 400A Frame, 250A Trip" → Frame=400, Trip=250
- Any other format

Extract:
- Frame rating (physical bucket size) - look for "AF" or "Frame"
- Trip rating (actual breaker) - look for "AT", "AS", "AE", or "Trip"
- Protection type if present (LSI, LS, LSIG)

**WIRE SPECIFICATIONS:**
- "600 kcmil", "#1/0", "(3) #2 AWG"
- "(2 PARALLEL SETS 3-3/C #600 KCMIL)"
- Any size notation

**PANEL LABELS:**
- "PP-1", "LP-2", "RP-3", "MDP", etc.
- Could be in any block

**EQUIPMENT RATINGS:**
- "800A", "110A", "225AF", etc.
- Look for amperage values

═══════════════════════════════════════════════════════════════
YOUR TASK:
═══════════════════════════════════════════════════════════════

1. ANALYZE THE BLOCKS ABOVE
   - What pattern do you see for bucket notation?
   - Identify ALL buckets with their frame and trip ratings

2. FOR EACH BUCKET IDENTIFIED:
   - Extract Frame rating (ignore for panel sizing)
   - Extract Trip rating (USE THIS for panel rating)
   - Note protection type if present

3. MATCH TO STRUCTURE:
   - Connection lines show what connects where
   - Text blocks near lines = specs for that feeder
   - Build complete bucket → feeder → panel map

4. VALIDATE:
   - Wire ampacity ≥ trip rating
   - Ground wire sized per NEC 250.122
   - Parallel sets calculated correctly

═══════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════

## PARSING RESULTS:

**BUCKET FORMAT DETECTED:** [Describe the pattern you identified]

**SWITCHBOARD BUCKETS:**

Bucket 1: [Extracted from blocks]
- Frame: [X]AF
- Trip: [Y]AT/AS/AE ← USE THIS
- Panel Rating: [Y]A (from trip, not frame)
- Feeder: [Wire specs from nearby connection]

Bucket 2: [Pattern]
- Frame: [X]AF
- Trip: [Y]AT/AS/AE
- Panel Rating: [Y]A
- Feeder: [Specs]

[Continue for all buckets found...]

## VALIDATION:
✓/✗ All ratings based on trip (not frame)
✓/✗ Wire sizing validated
✓/✗ Ground wire per NEC

Begin analysis. Parse the assembled blocks above to extract ALL equipment data.
"""
        
        return prompt


def analyze_drawing(image_path: str, trade: str = "electrical") -> str:
    """
    Main entry point for integrated drawing analysis
    
    Args:
        image_path: Path to drawing image
        trade: Type of trade (electrical, mechanical, plumbing, fire_protection)
    
    Returns:
        Complete analysis as string
    """
    agent = IntegratedDrawingAgent(image_path, trade)
    analysis = agent.analyze()
    
    # Display results
    console.print("\n" + "="*70)
    console.print(Panel.fit(
        "[bold green]ANALYSIS COMPLETE[/bold green]",
        border_style="green"
    ))
    console.print("="*70)
    console.print(analysis)
    console.print("="*70)
    
    return analysis


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        console.print("[red]Usage: python integrated_agent.py <image_path> [trade][/red]")
        console.print("Example: python integrated_agent.py SLD.png electrical")
        sys.exit(1)
    
    image_path = sys.argv[1]
    trade = sys.argv[2] if len(sys.argv) > 2 else "electrical"
    
    analyze_drawing(image_path, trade)
