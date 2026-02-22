"""
Construction Drawing Symbol Recognition - All Trades
Teaching AI to identify equipment by visual symbols, labels, and context
NOT by position or assumptions
"""

# ═══════════════════════════════════════════════════════════════
# ELECTRICAL SYMBOLS & IDENTIFICATION
# ═══════════════════════════════════════════════════════════════

ELECTRICAL_SYMBOLS = {
    "equipment": {
        "switchboard": {
            "symbols": [
                "Large rectangle with diagonal lines inside",
                "Rectangle with vertical bars/sections",
                "Box with 'SB' or 'SWBD' label"
            ],
            "labels": ["SWITCHBOARD", "MSB", "SWBD", "SB", "MAIN SWITCHBOARD", "ESB", "DSB"],
            "characteristics": [
                "Multiple feeders leaving (3+ lines exiting)",
                "Large incoming feeder (250+ kcmil typical)",
                "Ground wire #1/0 or larger",
                "Rating 400A-4000A typical"
            ],
            "context_clues": [
                "Fed by service entrance or transformer",
                "Distributes to multiple panels",
                "Often has 'MAIN' in label"
            ]
        },
        
        "switchgear": {
            "symbols": [
                "Large rectangle with sections/compartments drawn",
                "Multiple vertical divisions inside rectangle"
            ],
            "labels": ["SWITCHGEAR", "SWGR", "MAIN SWITCHGEAR", "MSG"],
            "characteristics": [
                "Very large incoming feeder (500+ kcmil)",
                "Multiple large outgoing feeders",
                "Rating 1000A-4000A+ typical",
                "May show bus bars graphically"
            ]
        },
        
        "panelboard": {
            "symbols": [
                "Smaller rectangle",
                "Rectangle with circuit lines inside",
                "Box with panel designation"
            ],
            "labels": ["PP-1", "LP-1", "RP-1", "PANEL", "PANELBOARD", "MDP", "DP"],
            "label_patterns": [
                "PP-# (Power Panel)",
                "LP-# (Lighting Panel)",
                "RP-# (Receptacle Panel)",
                "DP-# (Distribution Panel)",
                "MDP (Main Distribution Panel)"
            ],
            "characteristics": [
                "Fed by feeder (#1/0 to 500 kcmil typical)",
                "Feeds branch circuits (#12, #14)",
                "Rating 100A-400A typical",
                "Single feeder in, multiple circuits out"
            ]
        },
        
        "transformer": {
            "symbols": [
                "Two circles side by side with coils",
                "Circle with 'T' inside",
                "Rectangle with transformer windings drawn",
                "Two parallel vertical lines (schematic)"
            ],
            "labels": ["XFMR", "TRANSFORMER", "T-1", "TRANS", "DRY TYPE TRANSFORMER"],
            "characteristics": [
                "Shows primary voltage (input)",
                "Shows secondary voltage (output)",
                "kVA rating (45kVA, 75kVA, 112.5kVA, etc.)",
                "May show % impedance",
                "Voltage step-down or step-up notation (480V → 208V)"
            ],
            "context_clues": [
                "Fed from high voltage (480V, 4160V)",
                "Feeds low voltage (208V, 240V)",
                "Shows delta or wye connections"
            ]
        },
        
        "disconnect": {
            "symbols": [
                "Square with diagonal line (open switch)",
                "Box with 'DS' or 'DISC'",
                "Rectangle with switch symbol"
            ],
            "labels": ["DS", "DISCONNECT", "DISC", "SAFETY SWITCH", "FUSED DISCONNECT"],
            "characteristics": [
                "Amperage rating (30A, 60A, 100A, 200A, etc.)",
                "Fused or non-fused",
                "NEMA type (1, 3R, 4X, etc.)",
                "Located before equipment for isolation"
            ]
        },
        
        "motor_control_center": {
            "symbols": [
                "Large rectangle with multiple compartments",
                "Sections labeled with motor numbers"
            ],
            "labels": ["MCC", "MOTOR CONTROL CENTER"],
            "characteristics": [
                "Multiple motor starters shown",
                "Individual compartments numbered",
                "Large feeder in, multiple motor circuits out"
            ]
        },
        
        "automatic_transfer_switch": {
            "symbols": [
                "Two switches with logic symbol",
                "Box with 'ATS' label",
                "Transfer switch schematic"
            ],
            "labels": ["ATS", "AUTOMATIC TRANSFER SWITCH", "TRANSFER SWITCH"],
            "characteristics": [
                "Two sources (normal and emergency)",
                "Amperage rating",
                "Switching logic shown"
            ]
        },
        
        "generator": {
            "symbols": [
                "Circle with 'G' inside",
                "Generator symbol (rotating machine)"
            ],
            "labels": ["GEN", "GENERATOR", "EMERGENCY GENERATOR", "STANDBY GENERATOR"],
            "characteristics": [
                "kW rating (100kW, 250kW, 500kW, etc.)",
                "Voltage output (480V, 208V)",
                "Fuel type (diesel, gas, NG)"
            ]
        },
        
        "ups": {
            "symbols": [
                "Rectangle with 'UPS' label",
                "Battery symbol with inverter"
            ],
            "labels": ["UPS", "UNINTERRUPTIBLE POWER SUPPLY"],
            "characteristics": [
                "kVA or kW rating",
                "Battery backup time",
                "Input and output voltages"
            ]
        }
    },
    
    "conductors": {
        "feeder": {
            "visual": "Thick line or double line between equipment",
            "annotations": [
                "Wire size on or near line: (3) #1/0, (3) 250 kcmil",
                "Conduit size: 1-1/2 EMT, 2 RGS",
                "Ground wire: #6G, #8 GND"
            ],
            "recognition": "Connects major equipment (switchboard to panel)"
        },
        
        "branch_circuit": {
            "visual": "Thin line from panel to load",
            "annotations": [
                "Small wire size: #12, #14",
                "Circuit number: CKT 1, CKT 2",
                "Small conduit: 1/2, 3/4"
            ],
            "recognition": "Connects panel to final loads (lights, receptacles)"
        },
        
        "home_run": {
            "visual": "Line with arrow pointing to panel",
            "symbol": "Arrow or slash marks indicating destination",
            "annotations": [
                "Panel designation at arrow",
                "Circuit numbers"
            ]
        }
    },
    
    "power_flow_indicators": {
        "arrows": "Show direction of power flow",
        "line_thickness": "Thicker = larger capacity",
        "connections": "Lines ending at equipment boxes = connections"
    }
}

# ═══════════════════════════════════════════════════════════════
# MECHANICAL/HVAC SYMBOLS
# ═══════════════════════════════════════════════════════════════

MECHANICAL_SYMBOLS = {
    "equipment": {
        "air_handler": {
            "symbols": [
                "Rectangle with 'AHU' inside",
                "Box with fan symbol",
                "Rectangle showing coils and fan"
            ],
            "labels": ["AHU", "AIR HANDLER", "AIR HANDLING UNIT"],
            "characteristics": [
                "CFM capacity (1000 CFM, 5000 CFM, etc.)",
                "Supply and return duct connections",
                "May show heating/cooling coils"
            ]
        },
        
        "rooftop_unit": {
            "symbols": [
                "Rectangle with 'RTU' inside",
                "Box on roof outline"
            ],
            "labels": ["RTU", "ROOFTOP UNIT", "PACKAGE UNIT"],
            "characteristics": [
                "Tonnage (5 TON, 10 TON, 15 TON, etc.)",
                "Supply duct size",
                "Return duct size",
                "Located on roof (per name)"
            ]
        },
        
        "exhaust_fan": {
            "symbols": [
                "Circle with fan blades",
                "Square with 'EF' inside"
            ],
            "labels": ["EF", "EXHAUST FAN", "EF-1"],
            "characteristics": [
                "CFM rating",
                "Duct size",
                "Location (roof, wall, etc.)"
            ]
        },
        
        "vav_box": {
            "symbols": [
                "Small rectangle on duct",
                "Box with 'VAV' label"
            ],
            "labels": ["VAV", "VARIABLE AIR VOLUME"],
            "characteristics": [
                "CFM range (min/max)",
                "Damper type",
                "Reheat coil if applicable"
            ]
        },
        
        "diffuser": {
            "symbols": [
                "Square with X inside (supply)",
                "Square with circle (return)",
                "Triangle (exhaust)"
            ],
            "labels": ["SD (supply)", "RD (return)", "EG (exhaust grille)"],
            "annotations": [
                "Size: 24x24, 12x12, etc.",
                "CFM: 100, 200, etc."
            ]
        },
        
        "chiller": {
            "symbols": [
                "Large rectangle with 'CH' or 'CHILLER'",
                "Shows refrigerant cycle schematically"
            ],
            "labels": ["CH", "CHILLER", "CHILLED WATER PLANT"],
            "characteristics": [
                "Tonnage (100 TON, 500 TON, etc.)",
                "Type (water-cooled, air-cooled)",
                "Refrigerant type"
            ]
        },
        
        "boiler": {
            "symbols": [
                "Rectangle with 'B' or 'BOILER'",
                "Shows burner and heat exchanger"
            ],
            "labels": ["B", "BOILER", "HW BOILER"],
            "characteristics": [
                "BTU output",
                "Fuel type (gas, oil, electric)",
                "Pressure rating"
            ]
        }
    },
    
    "ductwork": {
        "supply_duct": {
            "visual": "Single line or rectangle with 'S' arrow",
            "annotations": [
                "Size: 24x12, 20x10, etc. (WxH)",
                "Round: 12Ø, 16Ø (diameter)",
                "CFM if shown"
            ]
        },
        
        "return_duct": {
            "visual": "Single line or rectangle with 'R' arrow",
            "annotations": "Same as supply, marked with R"
        },
        
        "exhaust_duct": {
            "visual": "Line with 'E' or 'EX' arrow",
            "annotations": "Size and CFM"
        }
    },
    
    "piping": {
        "chilled_water": {
            "visual": "Line with 'CHW' or 'CW' label",
            "annotations": "Pipe size: 2, 3, 4, 6, etc. (inches)"
        },
        
        "hot_water": {
            "visual": "Line with 'HW' or 'HHW' label",
            "annotations": "Pipe size and insulation notes"
        },
        
        "refrigerant": {
            "visual": "Line with 'REF' or refrigerant type (R-410A)",
            "annotations": [
                "Liquid line (LL): smaller diameter",
                "Suction line (SL): larger diameter"
            ]
        },
        
        "condensate": {
            "visual": "Dashed line with 'CD' label",
            "annotations": "Drain pipe size"
        }
    }
}

# ═══════════════════════════════════════════════════════════════
# PLUMBING SYMBOLS
# ═══════════════════════════════════════════════════════════════

PLUMBING_SYMBOLS = {
    "fixtures": {
        "water_closet": {
            "symbols": [
                "Oval or rectangle (plan view)",
                "Circle with 'WC' (riser)"
            ],
            "labels": ["WC", "WATER CLOSET", "TOILET"],
            "annotations": ["Flush valve or tank type"]
        },
        
        "lavatory": {
            "symbols": [
                "Rectangle or circle (plan view)",
                "Circle with 'LAV' (riser)"
            ],
            "labels": ["LAV", "LAVATORY", "SINK"],
            "annotations": ["Wall hung or counter mount"]
        },
        
        "urinal": {
            "symbols": [
                "Small rectangle or specific urinal shape",
                "Circle with 'UR' (riser)"
            ],
            "labels": ["UR", "URINAL"],
            "annotations": ["Wall hung or floor mount"]
        },
        
        "shower": {
            "symbols": [
                "Square with shower head symbol",
                "Circle with 'SH' (riser)"
            ],
            "labels": ["SH", "SHOWER"],
            "annotations": ["Dimensions, drain location"]
        },
        
        "floor_drain": {
            "symbols": [
                "Square with X",
                "Circle with 'FD'"
            ],
            "labels": ["FD", "FLOOR DRAIN"],
            "annotations": ["Size: 2, 3, 4, 6 inches"]
        },
        
        "drinking_fountain": {
            "symbols": [
                "Specific DF shape",
                "Circle with 'DF'"
            ],
            "labels": ["DF", "DRINKING FOUNTAIN", "WC (water cooler)"]
        }
    },
    
    "piping": {
        "cold_water": {
            "visual": "Solid line",
            "labels": ["CW", "COLD WATER"],
            "annotations": "Pipe size: 1/2, 3/4, 1, 1-1/4, 1-1/2, 2, 3, 4, etc."
        },
        
        "hot_water": {
            "visual": "Line with dashes",
            "labels": ["HW", "HOT WATER"],
            "annotations": "Pipe size and insulation"
        },
        
        "sanitary_drain": {
            "visual": "Heavy line",
            "labels": ["SAN", "SANITARY", "WASTE"],
            "annotations": [
                "Pipe size: 1-1/2, 2, 3, 4, 6, 8, etc.",
                "Slope: 1/4, 1/8 per foot",
                "Cleanout locations (CO)"
            ]
        },
        
        "vent": {
            "visual": "Thinner line than drain",
            "labels": ["V", "VENT"],
            "annotations": "Pipe size: 1-1/4, 1-1/2, 2, 3, 4"
        },
        
        "storm_drain": {
            "visual": "Line with 'ST' or 'SD' label",
            "labels": ["ST", "STORM", "SD"],
            "annotations": "Pipe size and slope"
        },
        
        "gas": {
            "visual": "Line with 'G' or gas symbol",
            "labels": ["G", "GAS", "NG (natural gas)"],
            "annotations": "Pipe size (usually small: 1/2, 3/4, 1)"
        }
    },
    
    "equipment": {
        "water_heater": {
            "symbols": [
                "Rectangle or circle with 'WH'",
                "Tank outline"
            ],
            "labels": ["WH", "WATER HEATER", "HWH"],
            "characteristics": [
                "Capacity (gallons): 40, 50, 75, 120, etc.",
                "Input BTU",
                "Recovery rate",
                "Gas or electric"
            ]
        },
        
        "backflow_preventer": {
            "symbols": [
                "Specific valve symbol",
                "Box with 'BFP' or 'RP'"
            ],
            "labels": ["BFP", "BACKFLOW PREVENTER", "RP", "RPZ"],
            "characteristics": "Pipe size, type (RPZ, DC, etc.)"
        },
        
        "water_softener": {
            "symbols": ["Tank shape with 'WS'"],
            "labels": ["WS", "WATER SOFTENER"],
            "characteristics": "Capacity in grains"
        }
    }
}

# ═══════════════════════════════════════════════════════════════
# FIRE PROTECTION SYMBOLS
# ═══════════════════════════════════════════════════════════════

FIRE_PROTECTION_SYMBOLS = {
    "sprinkler_heads": {
        "pendent": {
            "symbol": "Circle with downward stem",
            "labels": ["P", "PEND", "PENDENT"]
        },
        
        "upright": {
            "symbol": "Circle with upward stem",
            "labels": ["U", "UP", "UPRIGHT"]
        },
        
        "sidewall": {
            "symbol": "Half circle",
            "labels": ["SW", "SIDEWALL"]
        },
        
        "concealed": {
            "symbol": "Circle with C",
            "labels": ["C", "CONC", "CONCEALED"]
        }
    },
    
    "piping": {
        "sprinkler_main": {
            "visual": "Heavy line",
            "annotations": [
                "Pipe size: 1, 1-1/4, 1-1/2, 2, 2-1/2, 3, 4, 6, 8",
                "Number of heads served",
                "Flow direction arrows"
            ]
        },
        
        "branch_line": {
            "visual": "Line connecting heads to main",
            "annotations": "Pipe size and head count"
        }
    },
    
    "equipment": {
        "fire_pump": {
            "symbols": ["Pump symbol with 'FP'"],
            "labels": ["FP", "FIRE PUMP"],
            "characteristics": [
                "GPM capacity",
                "Pressure (psi)",
                "Driver type (electric, diesel)"
            ]
        },
        
        "fire_department_connection": {
            "symbols": ["FDC symbol - specific fire department connection"],
            "labels": ["FDC", "FIRE DEPARTMENT CONNECTION"],
            "characteristics": "Location and pipe size"
        },
        
        "post_indicator_valve": {
            "symbols": ["PIV symbol"],
            "labels": ["PIV", "POST INDICATOR VALVE"],
            "characteristics": "Size and location"
        }
    }
}

# ═══════════════════════════════════════════════════════════════
# STRUCTURAL SYMBOLS
# ═══════════════════════════════════════════════════════════════

STRUCTURAL_SYMBOLS = {
    "members": {
        "steel_beam": {
            "symbols": ["I-shape in section, labeled on plans"],
            "labels": [
                "W-shapes: W12x53, W18x86, W24x104",
                "Wide flange beam designations"
            ],
            "annotations": "Beam mark numbers (B1, B2, etc.)"
        },
        
        "steel_column": {
            "symbols": ["Square or circular column symbol"],
            "labels": [
                "W-shapes for heavy: W14x90",
                "HSS (hollow structural section): HSS8x8x1/2"
            ],
            "annotations": "Column mark numbers (C1, C2, etc.)"
        },
        
        "concrete_beam": {
            "symbols": ["Rectangular section"],
            "labels": ["B1, B2 (with dimensions like 12x24)"],
            "annotations": [
                "Width x Depth",
                "Reinforcement (#4@12, etc.)"
            ]
        },
        
        "concrete_column": {
            "symbols": ["Square or round column"],
            "labels": ["C1, C2 (with dimensions)"],
            "annotations": [
                "Column size: 12x12, 18x18, 24Ø",
                "Reinforcement pattern"
            ]
        },
        
        "joist": {
            "symbols": ["Parallel lines showing joist layout"],
            "labels": [
                "Open web joists: 16K4, 22K9",
                "Wood joists: 2x10@16 O.C."
            ]
        },
        
        "slab": {
            "symbols": ["Hatching or solid fill"],
            "labels": ["SOG (slab on grade)", "Floor slab"],
            "annotations": [
                "Thickness: 4, 6, 8 inches",
                "Reinforcement mesh or bars"
            ]
        }
    },
    
    "foundations": {
        "footing": {
            "symbols": ["Rectangle in section, square in plan"],
            "labels": ["F1, F2 (with dimensions)"],
            "annotations": "Size and reinforcement"
        },
        
        "pile": {
            "symbols": ["Circle with cross or pile symbol"],
            "labels": ["P (with pile designation)"],
            "annotations": "Pile type and capacity"
        }
    }
}

# ═══════════════════════════════════════════════════════════════
# EQUIPMENT IDENTIFICATION LOGIC
# ═══════════════════════════════════════════════════════════════

IDENTIFICATION_RULES = """
HOW TO IDENTIFY EQUIPMENT (NOT BY POSITION):

1. READ LABELS FIRST
   - Look for text inside or near symbols
   - Labels are most reliable: "SWITCHBOARD", "PP-1", "AHU-1"
   
2. RECOGNIZE SYMBOLS
   - Match visual symbol to library (rectangle with bars = switchboard)
   - Symbols are standardized but can vary by engineer
   
3. CHECK WIRE/PIPE SIZES
   - Large wires (500+ kcmil) = main equipment (switchboard, service)
   - Medium wires (#1/0 to 4/0) = feeders to panels
   - Small wires (#12, #14) = branch circuits
   - Ground wire size reveals equipment rating
   
4. ANALYZE CONNECTIONS
   - Equipment with ONE incoming feeder, MANY outgoing = distribution (panel/switchboard)
   - Equipment with MANY incoming lines, ONE outgoing = combining (paralleled equipment)
   - Equipment between two sources = transfer switch
   
5. USE CONTEXT CLUES
   - Voltage transformation shown = transformer
   - Two power sources shown = ATS or paralleling
   - Rotating equipment symbol = motor or generator
   
6. VERIFY WITH MULTIPLE SIGNALS
   - Don't rely on ONE indicator
   - Combine: label + symbol + wire size + connections = confident ID

DO NOT ASSUME BY POSITION:
- Top ≠ necessarily main equipment
- Left ≠ necessarily source
- Large box ≠ necessarily most important

EXAMPLE:
"I see a rectangle labeled 'MSB' with diagonal lines inside, fed by 600 kcmil 
with #1/0 ground, distributing to 4 smaller panels via #1/0 feeders.

Label: MSB = Main Switchboard ✓
Symbol: Rectangle with diagonal lines = Switchboard ✓  
Wire: 600 kcmil incoming = Main equipment ✓
Ground: #1/0 = 800A rating ✓
Connections: One in, multiple out = Distribution ✓

CONCLUSION: This is the 800A main switchboard."
"""
