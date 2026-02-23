"""
Agentic Drawing Analyzer for Fieldwise AI
Claude autonomously examines electrical drawings using tools to zoom, enhance, and extract data

NOW WITH OPENCV PREPROCESSING FOR STRUCTURAL DETECTION
"""

import anthropic
import base64
import json
from PIL import Image
import io
from typing import Dict, List, Optional, Tuple

# Import comprehensive trade knowledge and validation
from trade_knowledge import (
    ELECTRICAL_WIRE_AMPACITY,
    ELECTRICAL_BREAKER_WIRE_RULES,
    ELECTRICAL_GROUND_WIRE_SIZING,
    HVAC_DUCT_SIZING,
    HVAC_ROUND_DUCT_SIZING,
    HVAC_CFM_PER_TON,
    PLUMBING_FIXTURE_UNITS,
    PLUMBING_WATER_PIPE_SIZING,
    PLUMBING_DRAIN_PIPE_SIZING,
    FIRE_SPRINKLER_SPACING,
    FIRE_SPRINKLER_PIPE_SIZING,
    validate_electrical_circuit,
    validate_hvac_duct,
    validate_plumbing_pipe,
    validate_fire_sprinkler,
)

# Import symbol recognition
from construction_symbols import (
    ELECTRICAL_SYMBOLS,
    MECHANICAL_SYMBOLS,
    PLUMBING_SYMBOLS,
    FIRE_PROTECTION_SYMBOLS,
    STRUCTURAL_SYMBOLS,
    IDENTIFICATION_RULES,
)

# Import deep blueprint literacy
from blueprint_literacy_deep import (
    CORE_UNDERSTANDING,
    SYSTEMATIC_SCAN,
    GRAPHICAL_VS_TABULAR,
    SPATIAL_REASONING,
    COMPLEXITY_DETECTION,
    VALIDATION_MINDSET,
    COMPLETION_CHECKLIST,
)

# Import OpenCV preprocessing
from drawing_preprocessor import preprocess_electrical_drawing

# Initialize Anthropic client
API_KEY = "your-api-key-here"  # Replace with your actual API key
client = anthropic.Anthropic(api_key="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")


class DrawingAnalyzerAgent:
    """
    Autonomous agent that analyzes construction drawings
    Claude uses tools to zoom, enhance, and extract detailed information
    """
    
    # NEC Chapter 9 Table 5 - Conduit fill areas (40% fill for 3+ conductors)
    CONDUIT_FILL_AREA = {
        # EMT conduit sizes (in²) at 40% fill
        "1/2": 0.122,
        "3/4": 0.213,
        "1": 0.346,
        "1-1/4": 0.598,
        "1-1/2": 0.814,
        "2": 1.342,
        "2-1/2": 2.343,
        "3": 3.538,
        "3-1/2": 4.618,
        "4": 5.858,
    }
    
    # NEC Chapter 9 Table 8 - Wire cross-sectional areas (in² including insulation)
    WIRE_AREA_THHN = {
        # AWG sizes
        "14": 0.0097,
        "12": 0.0133,
        "10": 0.0211,
        "8": 0.0366,
        "6": 0.0507,
        "4": 0.0824,
        "3": 0.0973,
        "2": 0.1158,
        "1": 0.1562,
        # Ought sizes
        "1/0": 0.1855,
        "2/0": 0.2223,
        "3/0": 0.2679,
        "4/0": 0.3237,
        # MCM sizes
        "250": 0.3904,
        "300": 0.4536,
        "350": 0.5113,
        "400": 0.5863,
        "500": 0.7073,
        "600": 0.8316,
        "750": 1.0532,
        "1000": 1.3478,
    }
    
    def validate_conduit_fill(self, conduit_size: str, wires: list) -> dict:
        """
        Validate if wire configuration fits in conduit per NEC Chapter 9
        
        Args:
            conduit_size: e.g., "1/2", "1-1/2", "2"
            wires: list of dicts with 'size' and 'count'
                   e.g., [{'size': '1/0', 'count': 3}, {'size': '6', 'count': 1}]
        
        Returns:
            dict with validation result and details
        """
        # Normalize conduit size
        conduit_size = conduit_size.replace('"', '').replace(' ', '').strip()
        
        # Get conduit fill area
        if conduit_size not in self.CONDUIT_FILL_AREA:
            return {
                "valid": None,
                "error": f"Unknown conduit size: {conduit_size}",
                "message": "Cannot validate - conduit size not in NEC tables"
            }
        
        conduit_area = self.CONDUIT_FILL_AREA[conduit_size]
        
        # Calculate total wire area
        total_wire_area = 0
        wire_details = []
        
        for wire in wires:
            wire_size = wire['size'].replace('#', '').strip()
            wire_count = wire['count']
            
            if wire_size not in self.WIRE_AREA_THHN:
                return {
                    "valid": None,
                    "error": f"Unknown wire size: {wire_size}",
                    "message": "Cannot validate - wire size not in NEC tables"
                }
            
            wire_area = self.WIRE_AREA_THHN[wire_size]
            total_area = wire_area * wire_count
            total_wire_area += total_area
            
            wire_details.append({
                "size": wire_size,
                "count": wire_count,
                "area_each": round(wire_area, 4),
                "area_total": round(total_area, 4)
            })
        
        # Calculate fill percentage
        fill_percentage = (total_wire_area / conduit_area) * 100
        
        # NEC allows 40% fill for 3+ conductors
        is_valid = fill_percentage <= 100  # We use 40% table, so <100% of that is valid
        
        result = {
            "valid": is_valid,
            "conduit_size": conduit_size,
            "conduit_area": round(conduit_area, 4),
            "total_wire_area": round(total_wire_area, 4),
            "fill_percentage": round(fill_percentage, 1),
            "wire_details": wire_details,
            "message": ""
        }
        
        if not is_valid:
            result["message"] = f"⚠️ NEC VIOLATION: {fill_percentage:.1f}% fill exceeds 100% of allowable 40% fill. Conduit too small!"
            result["recommendation"] = self._recommend_conduit_size(wires)
        else:
            result["message"] = f"✓ Valid: {fill_percentage:.1f}% fill"
        
        return result
    
    def _recommend_conduit_size(self, wires: list) -> str:
        """Find minimum conduit size that works for given wires"""
        for size in ["1/2", "3/4", "1", "1-1/4", "1-1/2", "2", "2-1/2", "3", "4"]:
            result = self.validate_conduit_fill(size, wires)
            if result.get("valid"):
                return f"Minimum conduit size: {size}\" EMT"
        return "Requires conduit larger than 4\" EMT"
    
    def __init__(self, image_path: str, trade: str = "electrical"):
        """
        Initialize the agent with a drawing
        
        Args:
            image_path: Path to the drawing image (PNG, JPG)
            trade: Type of trade (electrical, mechanical, plumbing)
        """
        self.image_path = image_path
        self.trade = trade
        self.original_image = Image.open(image_path)
        self.conversation_history = []
        self.max_iterations = 50  # Allow exhaustive analysis - we're building the best
        
        # PREPROCESSING: Detect drawing structure with OpenCV
        print("\n🔬 PREPROCESSING PHASE: Analyzing drawing structure...")
        self.topology = preprocess_electrical_drawing(image_path)
        
        # Extract key information from preprocessing
        self.equipment_boxes = self.topology['equipment_boxes']
        self.connection_lines = self.topology['connection_lines']
        self.main_equipment_idx = self.topology.get('main_equipment_idx')
        
        print(f"✓ Preprocessing complete:")
        print(f"  - Found {len(self.equipment_boxes)} equipment boxes")
        print(f"  - Found {len(self.connection_lines)} connection lines")
        if self.main_equipment_idx is not None:
            main_box = self.equipment_boxes[self.main_equipment_idx]
            print(f"  - Main equipment at ({main_box.x}, {main_box.y})")
        print()
        
    
    def get_tools(self) -> List[Dict]:
        """
        Define tools that Claude can use to analyze the drawing
        """
        return [
            {
                "name": "get_image_region",
                "description": "Crop and zoom into a specific region of the drawing to see details more clearly. Use this when you need to read small text, wire sizes, breaker ratings, or any details that aren't clear in the full image. Coordinates are in pixels from top-left corner (0,0).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "integer",
                            "description": "X coordinate of top-left corner of region (pixels from left edge)"
                        },
                        "y": {
                            "type": "integer",
                            "description": "Y coordinate of top-left corner of region (pixels from top edge)"
                        },
                        "width": {
                            "type": "integer",
                            "description": "Width of region to extract (pixels)"
                        },
                        "height": {
                            "type": "integer",
                            "description": "Height of region to extract (pixels)"
                        },
                        "zoom": {
                            "type": "number",
                            "description": "Zoom level (1.0 = normal, 2.0 = 2x zoom, 3.0 = 3x zoom, etc.)",
                            "default": 2.0
                        }
                    },
                    "required": ["x", "y", "width", "height"]
                }
            },
            {
                "name": "enhance_image",
                "description": "Apply image enhancement (contrast, sharpening) to make text more readable. Use this if text is blurry or low contrast.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "Which region to enhance: 'full' for entire image, or coordinates as 'x,y,width,height'"
                        },
                        "contrast": {
                            "type": "number",
                            "description": "Contrast multiplier (1.0 = normal, 2.0 = high contrast)",
                            "default": 1.5
                        },
                        "sharpen": {
                            "type": "boolean",
                            "description": "Whether to apply sharpening filter",
                            "default": True
                        }
                    },
                    "required": ["region"]
                }
            },
            {
                "name": "get_image_dimensions",
                "description": "Get the width and height of the full drawing in pixels. Use this first to understand the coordinate system before requesting specific regions.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "validate_conduit_fill",
                "description": "Validate if a wire configuration fits in a conduit per NEC Chapter 9 conduit fill tables. Use this to verify that extracted specifications are physically possible and code-compliant.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "conduit_size": {
                            "type": "string",
                            "description": "Conduit size (e.g., '1/2', '3/4', '1-1/2', '2')"
                        },
                        "wires": {
                            "type": "array",
                            "description": "List of wires in the conduit",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "size": {
                                        "type": "string",
                                        "description": "Wire size (e.g., '12', '1/0', '250', '6')"
                                    },
                                    "count": {
                                        "type": "integer",
                                        "description": "Number of conductors of this size"
                                    }
                                },
                                "required": ["size", "count"]
                            }
                        }
                    },
                    "required": ["conduit_size", "wires"]
                }
            },
            {
                "name": "validate_hvac_duct",
                "description": "Validate duct sizing for airflow per IMC. Checks if duct can handle CFM and if velocity is in acceptable range.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "width": {
                            "type": "integer",
                            "description": "Duct width in inches"
                        },
                        "height": {
                            "type": "integer",
                            "description": "Duct height in inches"
                        },
                        "cfm": {
                            "type": "integer",
                            "description": "Airflow in cubic feet per minute"
                        }
                    },
                    "required": ["width", "height", "cfm"]
                }
            },
            {
                "name": "validate_plumbing_pipe",
                "description": "Validate pipe sizing for plumbing fixture load per UPC/IPC.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pipe_size": {
                            "type": "number",
                            "description": "Pipe diameter in inches (e.g., 0.5, 0.75, 1, 1.5, 2, 3, 4)"
                        },
                        "fixture_units": {
                            "type": "number",
                            "description": "Total fixture units (WSFU for supply, DFU for drainage)"
                        },
                        "is_drain": {
                            "type": "boolean",
                            "description": "True for drain/waste pipes, False for water supply pipes"
                        }
                    },
                    "required": ["pipe_size", "fixture_units", "is_drain"]
                }
            },
            {
                "name": "validate_fire_sprinkler",
                "description": "Validate fire sprinkler pipe sizing per NFPA 13 pipe schedule.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pipe_size": {
                            "type": "number",
                            "description": "Pipe diameter in inches"
                        },
                        "head_count": {
                            "type": "integer",
                            "description": "Number of sprinkler heads on this pipe"
                        },
                        "hazard_class": {
                            "type": "string",
                            "description": "Hazard classification",
                            "enum": ["light_hazard", "ordinary_hazard_1", "ordinary_hazard_2", "extra_hazard"]
                        }
                    },
                    "required": ["pipe_size", "head_count"]
                }
            }
        ]
    
    
    def execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """
        Execute a tool that Claude requested
        
        Returns:
            Dict with tool result (image data or information)
        """
        print(f"\n[TOOL] Claude is using: {tool_name}")
        print(f"[TOOL] Parameters: {json.dumps(tool_input, indent=2)}")
        
        if tool_name == "get_image_dimensions":
            width, height = self.original_image.size
            return {
                "width": width,
                "height": height,
                "message": f"Drawing dimensions: {width}x{height} pixels"
            }
        
        elif tool_name == "get_image_region":
            # Extract and zoom into region
            x = tool_input["x"]
            y = tool_input["y"]
            width = tool_input["width"]
            height = tool_input["height"]
            zoom = tool_input.get("zoom", 2.0)
            
            # Crop region
            region = self.original_image.crop((x, y, x + width, y + height))
            
            # Apply zoom (resize)
            new_width = int(width * zoom)
            new_height = int(height * zoom)
            zoomed = region.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to base64 for Claude
            img_buffer = io.BytesIO()
            zoomed.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            print(f"[TOOL] Extracted region: ({x},{y}) {width}x{height}, zoomed {zoom}x")
            
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_base64
                }
            }
        
        elif tool_name == "enhance_image":
            # Apply image enhancement
            from PIL import ImageEnhance, ImageFilter
            
            region_spec = tool_input["region"]
            contrast_level = tool_input.get("contrast", 1.5)
            should_sharpen = tool_input.get("sharpen", True)
            
            # Determine which image to enhance
            if region_spec == "full":
                img_to_enhance = self.original_image.copy()
            else:
                # Parse coordinates
                coords = [int(c) for c in region_spec.split(",")]
                x, y, width, height = coords
                img_to_enhance = self.original_image.crop((x, y, x + width, y + height))
            
            # Apply contrast
            enhancer = ImageEnhance.Contrast(img_to_enhance)
            enhanced = enhancer.enhance(contrast_level)
            
            # Apply sharpening
            if should_sharpen:
                enhanced = enhanced.filter(ImageFilter.SHARPEN)
            
            # Convert to base64
            img_buffer = io.BytesIO()
            enhanced.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            print(f"[TOOL] Enhanced image with contrast={contrast_level}, sharpen={should_sharpen}")
            
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_base64
                }
            }
        
        elif tool_name == "validate_conduit_fill":
            # Validate conduit fill per NEC
            conduit_size = tool_input["conduit_size"]
            wires = tool_input["wires"]
            
            result = self.validate_conduit_fill(conduit_size, wires)
            
            print(f"[TOOL] Conduit Fill Validation:")
            print(f"       Conduit: {conduit_size}\" EMT")
            print(f"       Wires: {wires}")
            print(f"       Result: {result['message']}")
            
            return result
        
        elif tool_name == "validate_hvac_duct":
            # Validate HVAC duct sizing
            width = tool_input["width"]
            height = tool_input["height"]
            cfm = tool_input["cfm"]
            
            result = validate_hvac_duct(width, height, cfm)
            
            print(f"[TOOL] HVAC Duct Validation:")
            print(f"       Duct: {width}x{height}\"")
            print(f"       CFM: {cfm}")
            print(f"       Velocity: {result.get('velocity_fpm')} fpm")
            if result['errors']:
                print(f"       ⚠️ ERRORS: {result['errors']}")
            if result['warnings']:
                print(f"       ⚠ Warnings: {result['warnings']}")
            
            return result
        
        elif tool_name == "validate_plumbing_pipe":
            # Validate plumbing pipe sizing
            pipe_size = tool_input["pipe_size"]
            fixture_units = tool_input["fixture_units"]
            is_drain = tool_input["is_drain"]
            
            result = validate_plumbing_pipe(pipe_size, fixture_units, is_drain)
            
            pipe_type = "Drain" if is_drain else "Water"
            print(f"[TOOL] Plumbing Pipe Validation:")
            print(f"       Pipe: {pipe_size}\" {pipe_type}")
            print(f"       Load: {fixture_units} FU")
            if result['errors']:
                print(f"       ⚠️ ERRORS: {result['errors']}")
            if result['warnings']:
                print(f"       ⚠ Warnings: {result['warnings']}")
            
            return result
        
        elif tool_name == "validate_fire_sprinkler":
            # Validate fire sprinkler pipe sizing
            pipe_size = tool_input["pipe_size"]
            head_count = tool_input["head_count"]
            hazard_class = tool_input.get("hazard_class", "ordinary_hazard_1")
            
            result = validate_fire_sprinkler(pipe_size, head_count, hazard_class)
            
            print(f"[TOOL] Fire Sprinkler Validation:")
            print(f"       Pipe: {pipe_size}\"")
            print(f"       Heads: {head_count}")
            if result['errors']:
                print(f"       ⚠️ ERRORS: {result['errors']}")
            if result['warnings']:
                print(f"       ⚠ Warnings: {result['warnings']}")
            
            return result
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    
    def get_initial_prompt(self) -> str:
        """
        Get the initial prompt for Claude to start analyzing
        """
        
        # Build preprocessing summary for Claude
        preprocessing_summary = self._build_preprocessing_summary()
        
        if self.trade == "electrical":
            trade_knowledge = self._get_electrical_knowledge()
        elif self.trade == "mechanical" or self.trade == "hvac":
            trade_knowledge = self._get_mechanical_knowledge()
        elif self.trade == "plumbing":
            trade_knowledge = self._get_plumbing_knowledge()
        elif self.trade == "fire_protection":
            trade_knowledge = self._get_fire_protection_knowledge()
        else:
            trade_knowledge = "You are analyzing a construction drawing. Use tools to zoom and extract specifications."
        
        return f"""{preprocessing_summary}

{trade_knowledge}

Work methodically using the detected structure above. Zoom into each box and line to read specifications.

When confident, provide final analysis."""
    
    def _build_preprocessing_summary(self) -> str:
        """Build summary of OpenCV preprocessing results for Claude"""
        summary = f"""
═══════════════════════════════════════════════════════════════
PREPROCESSING RESULTS (OpenCV Structural Detection):
═══════════════════════════════════════════════════════════════

Drawing has been pre-analyzed. Here's what was detected:

EQUIPMENT BOXES DETECTED: {len(self.equipment_boxes)}
"""
        
        # List detected boxes with coordinates
        for idx, box in enumerate(self.equipment_boxes[:10]):  # Top 10 boxes
            marker = " ← LIKELY MAIN EQUIPMENT" if idx == self.main_equipment_idx else ""
            summary += f"\nBox #{idx}: Location ({box.x}, {box.y}), Size {box.width}x{box.height}{marker}"
        
        summary += f"\n\nCONNECTION LINES DETECTED: {len(self.connection_lines)}\n"
        
        # List lines with their connections
        for idx, line in enumerate(self.connection_lines[:15]):  # Top 15 lines
            conn_info = ""
            if line.source_box is not None and line.dest_box is not None:
                conn_info = f" (Connects Box #{line.source_box} → Box #{line.dest_box})"
            elif line.source_box is not None:
                conn_info = f" (From Box #{line.source_box})"
            elif line.dest_box is not None:
                conn_info = f" (To Box #{line.dest_box})"
            
            text_info = ""
            if line.text_region:
                tx, ty, tw, th = line.text_region
                text_info = f" - TEXT NEAR LINE at ({tx},{ty})"
            
            summary += f"\nLine #{idx}: ({line.x1},{line.y1}) to ({line.x2},{line.y2}){conn_info}{text_info}"
        
        summary += f"""

═══════════════════════════════════════════════════════════════
YOUR TASK: Use this structural information to guide your analysis.

PRIORITY TARGETS:
1. Box #{self.main_equipment_idx if self.main_equipment_idx is not None else 0} (likely main equipment) - ZOOM AND READ LABEL
2. Lines connecting boxes - ZOOM ON TEXT REGIONS to read wire specs
3. All other boxes - identify each piece of equipment

DO NOT waste iterations on random areas. Use these coordinates to zoom directly to equipment and connection specs.
═══════════════════════════════════════════════════════════════
"""
        return summary
    
    def _get_electrical_knowledge(self) -> str:
        return f"""
═══════════════════════════════════════════════════════════════
YOU ARE A PROFESSIONAL ELECTRICAL ENGINEER WITH 20+ YEARS EXPERIENCE
═══════════════════════════════════════════════════════════════

{CORE_UNDERSTANDING}

{SYSTEMATIC_SCAN}

{GRAPHICAL_VS_TABULAR}

{COMPLEXITY_DETECTION}

═══════════════════════════════════════════════════════════════
ELECTRICAL-SPECIFIC READING STRATEGY:
═══════════════════════════════════════════════════════════════

THIS IS A SINGLE LINE DIAGRAM. It shows ELECTRICAL CONNECTIONS.

KEY COMPONENTS TO IDENTIFY:

1. EQUIPMENT (Boxes/rectangles/symbols):
   Switchboards: {ELECTRICAL_SYMBOLS['equipment']['switchboard']['labels']}
   Panels: {ELECTRICAL_SYMBOLS['equipment']['panelboard']['label_patterns']}
   Transformers: {ELECTRICAL_SYMBOLS['equipment']['transformer']['labels']}

2. CONNECTIONS (Lines between equipment):
   Lines = Feeders/conductors
   Text ON lines = Wire specifications
   THIS IS WHERE CRITICAL DATA IS

3. SCHEDULES (Tables):
   Circuit breakdowns
   Branch circuit details
   Separate from main distribution

═══════════════════════════════════════════════════════════════
WIRE SIZE AS SYSTEM IDENTIFIER:
═══════════════════════════════════════════════════════════════

600-1000 kcmil → MAIN SERVICE (switchboard incoming)
250-500 kcmil → LARGE DISTRIBUTION (switchboard to sub-distribution)
#1/0 to #4/0 → PANEL FEEDERS (switchboard to panels) ← LOOK FOR THIS
#6 to #2 → SUB-FEEDERS (smaller distribution)
#12, #14 → BRANCH CIRCUITS (panel to loads)
22-18 AWG → CONTROL CIRCUITS (separate system)

IF YOU SEE MULTIPLE WIRE SIZE RANGES → MULTIPLE SYSTEMS PRESENT

Example: 600 kcmil + #1/0 + 22 AWG on same sheet =
- Main service (600 kcmil)
- Panel feeders (#1/0) 
- Control circuits (22 AWG)
ALL THREE must be analyzed separately.

═══════════════════════════════════════════════════════════════
GROUND WIRE = EQUIPMENT RATING:
═══════════════════════════════════════════════════════════════

#1/0 ground → 800A equipment
#4/0 ground → 1600A equipment
#6 ground → 200A equipment  
#8 ground → 100A equipment

Use this to IDENTIFY equipment even if label is unclear.

═══════════════════════════════════════════════════════════════
MANDATORY ANALYSIS WORKFLOW:
═══════════════════════════════════════════════════════════════

PHASE 1: COMPLETE SHEET SCAN (Overview zoom 1x)
- Count ALL equipment boxes/symbols
- Count ALL connection lines
- Note ALL wire sizes mentioned (kcmil, #1/0, #12, 22 AWG, etc.)
- Identify ALL schedules/tables

PHASE 2: EQUIPMENT IDENTIFICATION (Zoom 4-5x on EACH box)
- Read label in each box
- Identify type (switchboard? panel? transformer?)
- Note size indicators (voltage, amperage if shown)

PHASE 3: CONNECTION TRACING (Zoom 5-6x on EACH line)
- For EVERY line connecting equipment:
  * Zoom on the LINE itself
  * Read text ON or NEAR the line
  * Record: wire size, conductor count, ground, conduit
  * Identify: what it connects (source → destination)

PHASE 4: SCHEDULE ANALYSIS (Zoom on tables)
- Read circuit schedules
- Identify: branch circuits vs feeders
- Separate: power vs control vs data

PHASE 5: SYSTEM SEPARATION
- Group by wire size:
  * Large wires (kcmil/#1/0) = POWER DISTRIBUTION
  * Small wires (#12/#14) = BRANCH CIRCUITS
  * Control wires (22 AWG) = CONTROL SYSTEMS
  * Data cable (CAT 6) = DATA SYSTEMS

{VALIDATION_MINDSET}

═══════════════════════════════════════════════════════════════
BEFORE YOU CONCLUDE - MANDATORY CHECKLIST:
═══════════════════════════════════════════════════════════════

{COMPLETION_CHECKLIST}

IF YOU CANNOT CHECK ALL BOXES → YOU ARE NOT DONE

COMMON FAILURE MODES TO AVOID:

❌ "I see 22 AWG circuits, this is a control system" → STOPPED TOO EARLY
✓ "I see 22 AWG circuits AND I searched for kcmil feeders AND I found the switchboard"

❌ "I read the schedule table, analysis complete" → IGNORED GRAPHICAL PORTION
✓ "I read the schedule AND traced all equipment connections AND read feeder specs"

❌ "This is clearly just X" → ASSUMED WITHOUT SYSTEMATIC SEARCH
✓ "After checking every zone, every line, every box, I found systems X, Y, and Z"

═══════════════════════════════════════════════════════════════
VALIDATION CHECKS:
═══════════════════════════════════════════════════════════════

After analysis, verify using conduit fill calculations:
- validate_conduit_fill for each feeder
- If validation fails → You misread the size (1/2 vs 1-1/2 common error)
- Re-zoom at 6x and re-read

═══════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════

SYSTEM 1: POWER DISTRIBUTION (if present)

MAIN SWITCHBOARD [label]:
- Rating: [from ground wire]
- Fed by: [incoming wire specs]
- Distributes to: [list all downstream equipment]

PANEL [name]:
- Rating: [from ground wire]
- Fed by: [wire specs ON the line] from [source equipment]

PANEL [name]:
- Rating: [from ground wire]
- Fed by: [wire specs ON the line] from [source equipment]

SYSTEM 2: BRANCH CIRCUITS (if present in schedules)
[Circuit details from schedules]

SYSTEM 3: CONTROL CIRCUITS (if present)
[22 AWG control circuits]

SYSTEM 4: DATA/COMMUNICATIONS (if present)
[CAT 6, fiber, etc.]

═══════════════════════════════════════════════════════════════

REMEMBER: You are a PROFESSIONAL. Be SYSTEMATIC. Be THOROUGH. Be ACCURATE.
"""
    
    def _get_mechanical_knowledge(self) -> str:
        return """
CRITICAL: You are an expert mechanical/HVAC engineer analyzing construction drawings.

═══════════════════════════════════════════════════════════════
DUCT SIZING - IMC 2021 & ASHRAE:
═══════════════════════════════════════════════════════════════
Rectangular Ducts: Read as WIDTHxHEIGHT (e.g., "12x8" = 12" wide × 8" high)
Round Ducts: Read diameter (e.g., "10Ø" = 10" diameter)

Common Sizes:
- Small: 6x6, 8x8, 10x10, 12x12
- Medium: 14x14, 16x16, 18x18, 20x20
- Large: 24x24, 30x30, 36x36

AIRFLOW RULES:
- Target velocity: 600-2000 fpm (feet per minute)
- CFM per ton cooling: ~400 CFM/ton standard
- High velocity = noise issues
- Low velocity = oversized duct

═══════════════════════════════════════════════════════════════
EQUIPMENT SIZING:
═══════════════════════════════════════════════════════════════
RTU (Rooftop Unit): Read tonnage (e.g., "10 TON RTU")
AHU (Air Handler): Read CFM capacity
VAV (Variable Air Volume): Read CFM range

Refrigerant Lines:
- Liquid line (smaller): 3/8", 1/2", 5/8", 7/8"
- Suction line (larger): 5/8", 7/8", 1-1/8", 1-3/8", 1-5/8"

VALIDATION TOOLS:
- validate_hvac_duct: Check duct can handle CFM and velocity is acceptable
- Use for all duct runs to verify sizing
"""
    
    def _get_plumbing_knowledge(self) -> str:
        return """
CRITICAL: You are an expert plumbing engineer analyzing construction drawings.

═══════════════════════════════════════════════════════════════
PIPE SIZING - UPC 2021 & IPC 2021:
═══════════════════════════════════════════════════════════════
Water Supply Pipes: 1/2", 3/4", 1", 1-1/4", 1-1/2", 2", 2-1/2", 3", 4"
Drain/Waste Pipes: 1-1/2", 2", 3", 4", 5", 6", 8", 10", 12"
Vent Pipes: 1-1/4", 1-1/2", 2", 2-1/2", 3", 4"

FIXTURE UNITS (FU):
- Water closet (tank): 3 WSFU
- Lavatory: 1 WSFU
- Shower: 2 WSFU
- Kitchen sink: 1.5 WSFU
- Dishwasher: 1.5 WSFU

DRAIN FIXTURE UNITS (DFU):
- Water closet: 4 DFU
- Lavatory: 1 DFU
- Shower: 2 DFU
- Kitchen sink: 2 DFU

PIPE SLOPE:
- 2" and smaller: 1/4" per foot minimum
- 3" to 6": 1/8" per foot minimum
- 8" and larger: 1/16" per foot minimum

VALIDATION TOOLS:
- validate_plumbing_pipe: Check pipe size vs fixture unit load
- Use separately for water supply (WSFU) and drains (DFU)
"""
    
    def _get_fire_protection_knowledge(self) -> str:
        return """
CRITICAL: You are an expert fire protection engineer analyzing construction drawings.

═══════════════════════════════════════════════════════════════
SPRINKLER SPACING - NFPA 13 (2022):
═══════════════════════════════════════════════════════════════
Maximum Spacing Between Heads:
- Light Hazard: 15 feet
- Ordinary Hazard: 15 feet
- Extra Hazard: 12 feet
- Extended Coverage: 20 feet (light hazard only)

Maximum Area Per Head:
- Light Hazard: 200 sq ft
- Ordinary Hazard: 130 sq ft
- Extra Hazard: 100 sq ft

PIPE SIZING (Schedule Method):
- 1" pipe: max 2 heads
- 1-1/4" pipe: max 3 heads
- 1-1/2" pipe: max 5 heads
- 2" pipe: max 10 heads
- 2-1/2" pipe: max 20 heads
- 3" pipe: max 40 heads
- 4" pipe: max 100 heads

DESIGN DENSITIES:
- Light Hazard: 0.10 gpm/sq ft
- Ordinary Hazard 1: 0.15 gpm/sq ft
- Ordinary Hazard 2: 0.20 gpm/sq ft
- Extra Hazard: 0.30-0.40 gpm/sq ft

VALIDATION TOOLS:
- validate_fire_sprinkler: Check pipe size vs head count per NFPA 13
- Use for all branch lines and mains
"""
    
    
    def image_to_base64(self, image: Image) -> str:
        """Convert PIL Image to base64 string"""
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        return base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    
    def analyze(self) -> str:
        """
        Run the agentic analysis loop
        
        Returns:
            Final analysis from Claude
        """
        print(f"\n{'='*60}")
        print(f"AGENTIC DRAWING ANALYSIS - {self.trade.upper()}")
        print(f"Drawing: {self.image_path}")
        print(f"{'='*60}\n")
        
        # Convert original image to base64
        original_base64 = self.image_to_base64(self.original_image)
        
        # Initialize conversation with the drawing and initial prompt
        self.conversation_history = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": original_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": self.get_initial_prompt()
                    }
                ]
            }
        ]
        
        # Agent loop
        for iteration in range(self.max_iterations):
            print(f"\n--- Iteration {iteration + 1}/{self.max_iterations} ---")
            
            # Call Claude with tools
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                tools=self.get_tools(),
                messages=self.conversation_history
            )
            
            print(f"[CLAUDE] Stop reason: {response.stop_reason}")
            
            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Extract tool uses from response
                tool_uses = [block for block in response.content if block.type == "tool_use"]
                
                # Build tool results
                tool_results = []
                
                for tool_use in tool_uses:
                    # Execute the tool
                    result = self.execute_tool(tool_use.name, tool_use.input)
                    
                    # Format for Claude
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": [result] if isinstance(result, dict) and "type" in result else [{"type": "text", "text": json.dumps(result)}]
                    })
                
                # Add assistant's response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Add tool results to history
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
            
            else:
                # Claude is done - extract final answer
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                
                print(f"\n{'='*60}")
                print(f"ANALYSIS COMPLETE")
                print(f"{'='*60}")
                
                return final_text
        
        # Max iterations reached
        print(f"\n[WARNING] Max iterations ({self.max_iterations}) reached")
        return "Analysis incomplete - max iterations reached"


def analyze_drawing(image_path: str, trade: str = "electrical") -> str:
    """
    Convenience function to analyze a drawing
    
    Args:
        image_path: Path to drawing image
        trade: Type of trade (electrical, mechanical, plumbing)
    
    Returns:
        Complete analysis from Claude
    """
    agent = DrawingAnalyzerAgent(image_path, trade)
    return agent.analyze()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python drawing_agent.py <path-to-drawing>")
        print("Example: python drawing_agent.py SLD.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    trade = sys.argv[2] if len(sys.argv) > 2 else "electrical"
    
    # Run analysis
    result = analyze_drawing(image_path, trade)
    
    # Print results
    print("\n" + "="*60)
    print("FINAL ANALYSIS:")
    print("="*60)
    print(result)
    print("="*60)
