"""
Trade Knowledge & Validation Rules for Fieldwise AI
Comprehensive engineering knowledge for all construction trades
"""

# ═══════════════════════════════════════════════════════════════
# ELECTRICAL - NEC 2023
# ═══════════════════════════════════════════════════════════════

ELECTRICAL_WIRE_AMPACITY = {
    # NEC Table 310.16 - 75°C column (most common)
    "14": 20,
    "12": 25,
    "10": 35,
    "8": 50,
    "6": 65,
    "4": 85,
    "3": 100,
    "2": 115,
    "1": 130,
    "1/0": 150,
    "2/0": 175,
    "3/0": 200,
    "4/0": 230,
    "250": 255,
    "300": 285,
    "350": 310,
    "400": 335,
    "500": 380,
    "600": 420,
    "750": 475,
    "1000": 545,
}

ELECTRICAL_BREAKER_WIRE_RULES = {
    # NEC 240.4(D) & 310.16 - Minimum wire size for breaker
    15: "14",
    20: "12",
    25: "10",
    30: "10",
    40: "8",
    50: "6",
    60: "6",
    70: "4",
    80: "4",
    90: "3",
    100: "3",
    110: "2",
    125: "1",
    150: "1/0",
    175: "2/0",
    200: "3/0",
    225: "4/0",
    250: "250",
    300: "300",
    350: "350",
    400: "400",
}

ELECTRICAL_GROUND_WIRE_SIZING = {
    # NEC 250.122 - Equipment grounding conductor sizing
    15: "14",
    20: "12",
    30: "10",
    40: "10",
    60: "10",
    100: "8",
    200: "6",
    300: "4",
    400: "3",
    500: "2",
    600: "1",
    800: "1/0",
    1000: "2/0",
    1200: "3/0",
    1600: "4/0",
    2000: "250",
}

ELECTRICAL_VOLTAGE_DROP_MAX = {
    # NEC 210.19(A) Informational Note No. 4
    "branch_circuit": 0.03,  # 3% max
    "feeder": 0.03,           # 3% max  
    "combined": 0.05,         # 5% max combined
}

# ═══════════════════════════════════════════════════════════════
# MECHANICAL/HVAC - IMC 2021 & ASHRAE
# ═══════════════════════════════════════════════════════════════

HVAC_DUCT_SIZING = {
    # CFM capacity for rectangular duct at 0.1" friction loss per 100ft
    # Format: (width, height): max_cfm
    (6, 6): 65,
    (6, 8): 95,
    (8, 8): 130,
    (8, 10): 165,
    (10, 10): 210,
    (10, 12): 260,
    (12, 12): 320,
    (12, 14): 380,
    (14, 14): 450,
    (14, 16): 525,
    (16, 16): 610,
    (16, 18): 700,
    (18, 18): 800,
    (20, 20): 1000,
    (24, 24): 1450,
    (30, 30): 2300,
}

HVAC_ROUND_DUCT_SIZING = {
    # Round duct diameter: max CFM at 0.1" friction
    4: 40,
    5: 65,
    6: 95,
    7: 130,
    8: 175,
    9: 225,
    10: 280,
    12: 410,
    14: 575,
    16: 775,
    18: 1015,
    20: 1300,
    24: 1900,
    30: 3000,
}

HVAC_REFRIGERANT_LINE_SIZING = {
    # Tonnage: (liquid_line_OD, suction_line_OD) in inches
    1.5: (3/8, 5/8),
    2.0: (3/8, 5/8),
    2.5: (3/8, 7/8),
    3.0: (3/8, 7/8),
    3.5: (3/8, 7/8),
    4.0: (1/2, 7/8),
    5.0: (1/2, 1.125),
    7.5: (5/8, 1.375),
    10.0: (5/8, 1.625),
    15.0: (7/8, 2.125),
    20.0: (7/8, 2.625),
}

HVAC_CFM_PER_TON = {
    "standard": 400,  # CFM per ton of cooling
    "hot_humid": 350,  # Lower for dehumidification
    "dry": 450,        # Higher for sensible cooling
}

# ═══════════════════════════════════════════════════════════════
# PLUMBING - UPC 2021 & IPC 2021
# ═══════════════════════════════════════════════════════════════

PLUMBING_FIXTURE_UNITS = {
    # Water supply fixture units (WSFU)
    "water_closet_tank": 3.0,
    "water_closet_flush": 6.0,
    "urinal": 3.0,
    "lavatory": 1.0,
    "shower": 2.0,
    "bathtub": 2.0,
    "kitchen_sink": 1.5,
    "dishwasher": 1.5,
    "washing_machine": 2.0,
    "hose_bibb": 2.5,
}

PLUMBING_WATER_PIPE_SIZING = {
    # Pipe size (inches): max WSFU capacity
    # Based on 40 psi pressure, 10 fps velocity
    1/2: 3,
    3/4: 6,
    1: 12,
    1.25: 19,
    1.5: 27,
    2: 44,
    2.5: 70,
    3: 102,
    4: 178,
    5: 280,
    6: 420,
}

PLUMBING_DRAIN_PIPE_SIZING = {
    # Pipe size (inches): max DFU (drainage fixture units)
    1.25: 1,
    1.5: 3,
    2: 6,
    3: 20,
    4: 160,
    5: 360,
    6: 620,
    8: 1400,
    10: 2500,
    12: 3900,
}

PLUMBING_VENT_SIZING = {
    # Based on DFU load and developed length
    # Format: (dfu, length_ft): min_vent_diameter
    (8, 50): 1.25,
    (8, 100): 1.5,
    (20, 50): 1.5,
    (20, 100): 2.0,
    (50, 50): 2.0,
    (50, 200): 2.5,
    (100, 100): 2.5,
    (100, 300): 3.0,
}

PLUMBING_PIPE_SLOPE = {
    # Minimum slope for drain pipes (inches per foot)
    2: 1/4,    # 2" and smaller: 1/4" per foot
    3: 1/8,    # 3" to 6": 1/8" per foot  
    4: 1/8,
    6: 1/8,
    8: 1/16,   # 8" and larger: 1/16" per foot
}

# ═══════════════════════════════════════════════════════════════
# FIRE PROTECTION - NFPA 13 (2022)
# ═══════════════════════════════════════════════════════════════

FIRE_SPRINKLER_SPACING = {
    # Maximum spacing between sprinklers (feet)
    "standard_coverage": {
        "light_hazard": 15,
        "ordinary_hazard_1": 15,
        "ordinary_hazard_2": 15,
        "extra_hazard": 12,
    },
    "extended_coverage": {
        "light_hazard": 20,
    }
}

FIRE_SPRINKLER_AREA_COVERAGE = {
    # Maximum area per sprinkler head (sq ft)
    "light_hazard": 200,
    "ordinary_hazard_1": 130,
    "ordinary_hazard_2": 130,
    "extra_hazard": 100,
}

FIRE_SPRINKLER_PIPE_SIZING = {
    # Pipe size: max number of sprinklers (Schedule 40 steel)
    # NFPA 13 pipe schedule method
    1: 2,
    1.25: 3,
    1.5: 5,
    2: 10,
    2.5: 20,
    3: 40,
    3.5: 65,
    4: 100,
    5: 160,
    6: 275,
    8: 400,
}

FIRE_SPRINKLER_DENSITIES = {
    # Design density (gpm/sq ft)
    "light_hazard": 0.10,
    "ordinary_hazard_1": 0.15,
    "ordinary_hazard_2": 0.20,
    "extra_hazard_1": 0.30,
    "extra_hazard_2": 0.40,
}

# ═══════════════════════════════════════════════════════════════
# STRUCTURAL - IBC 2021 & AISC
# ═══════════════════════════════════════════════════════════════

STRUCTURAL_BEAM_SPANS = {
    # Residential floor joists (40 psf live load, 10 psf dead load)
    # Format: (member_size, spacing_inches): max_span_feet
    ("2x6", 16): 9.8,
    ("2x8", 16): 12.9,
    ("2x10", 16): 16.5,
    ("2x12", 16): 19.9,
    ("2x6", 12): 11.2,
    ("2x8", 12): 14.7,
    ("2x10", 12): 18.8,
    ("2x12", 12): 22.7,
}

STRUCTURAL_STEEL_SECTIONS = {
    # Common W-shapes and their properties
    # Format: section: (depth_in, weight_plf, moment_capacity_kip_ft)
    "W8x31": (8, 31, 110),
    "W10x45": (10, 45, 200),
    "W12x53": (12, 53, 280),
    "W14x68": (14, 68, 420),
    "W16x77": (16, 77, 550),
    "W18x86": (18, 86, 710),
    "W21x93": (21, 93, 930),
    "W24x104": (24, 104, 1180),
}

STRUCTURAL_CONCRETE_STRENGTH = {
    # Common concrete strengths (psi)
    "residential": 2500,
    "commercial_slab": 3000,
    "commercial_structural": 4000,
    "high_rise": 5000,
    "prestressed": 6000,
}

# ═══════════════════════════════════════════════════════════════
# ARCHITECTURAL - IBC 2021
# ═══════════════════════════════════════════════════════════════

ARCH_EGRESS_REQUIREMENTS = {
    # Occupancy load factors (sq ft per person)
    "assembly_fixed_seats": 7,
    "assembly_standing": 5,
    "business": 100,
    "educational_classroom": 20,
    "industrial": 100,
    "mercantile_sales": 30,
    "residential": 200,
    "storage": 300,
}

ARCH_EXIT_WIDTH = {
    # Minimum exit width per occupant
    "stairs": 0.3,  # inches per person
    "other_egress": 0.2,  # inches per person
}

ARCH_DOOR_SIZES = {
    # Common door sizes (width x height in inches)
    "residential_interior": (30, 80),
    "residential_exterior": (36, 80),
    "commercial_single": (36, 84),
    "commercial_pair": (72, 84),
    "ada_compliant": (36, 80),
}

# ═══════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def validate_electrical_circuit(breaker_size, wire_size, wire_count, conduit_size, circuit_length=100):
    """Comprehensive electrical circuit validation"""
    errors = []
    warnings = []
    
    # 1. Wire ampacity vs breaker size
    wire_amp = ELECTRICAL_WIRE_AMPACITY.get(wire_size)
    if wire_amp and wire_amp < breaker_size:
        errors.append(f"NEC 240.4: Wire {wire_size} ({wire_amp}A) too small for {breaker_size}A breaker")
    
    # 2. Minimum wire size for breaker
    min_wire = ELECTRICAL_BREAKER_WIRE_RULES.get(breaker_size)
    if min_wire and compare_wire_size(wire_size, min_wire) < 0:
        errors.append(f"NEC 310.16: Minimum {min_wire} required for {breaker_size}A breaker")
    
    # 3. Voltage drop check (rough estimate)
    # Simplified - actual calculation needs more parameters
    if circuit_length > 100 and wire_size in ["14", "12", "10"]:
        warnings.append(f"Long circuit ({circuit_length}ft) - verify voltage drop calculation")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_hvac_duct(width, height, cfm):
    """Validate duct sizing for airflow"""
    errors = []
    warnings = []
    
    # Check if duct size can handle CFM
    max_cfm = HVAC_DUCT_SIZING.get((width, height))
    
    if max_cfm:
        if cfm > max_cfm:
            errors.append(f"IMC: {width}x{height} duct too small for {cfm} CFM (max {max_cfm} CFM)")
        elif cfm > max_cfm * 0.8:
            warnings.append(f"Duct operating near capacity ({cfm}/{max_cfm} CFM)")
    
    # Check velocity (should be 600-2000 fpm typically)
    area_sqft = (width * height) / 144
    velocity = cfm / area_sqft if area_sqft > 0 else 0
    
    if velocity > 2000:
        warnings.append(f"High velocity ({velocity:.0f} fpm) - may cause noise")
    elif velocity < 600:
        warnings.append(f"Low velocity ({velocity:.0f} fpm) - oversized duct")
    
    return {
        "valid": len(errors) == 0,
        "velocity_fpm": round(velocity),
        "errors": errors,
        "warnings": warnings
    }


def validate_plumbing_pipe(pipe_size, fixture_units, is_drain=False):
    """Validate pipe sizing for fixture load"""
    errors = []
    warnings = []
    
    if is_drain:
        max_fu = PLUMBING_DRAIN_PIPE_SIZING.get(pipe_size)
        code = "UPC Table 703.2"
    else:
        max_fu = PLUMBING_WATER_PIPE_SIZING.get(pipe_size)
        code = "UPC Table 610.3"
    
    if max_fu:
        if fixture_units > max_fu:
            errors.append(f"{code}: {pipe_size}\" pipe too small for {fixture_units} FU (max {max_fu} FU)")
        elif fixture_units > max_fu * 0.8:
            warnings.append(f"Pipe operating near capacity ({fixture_units}/{max_fu} FU)")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_fire_sprinkler(pipe_size, head_count, hazard_class="ordinary_hazard_1"):
    """Validate sprinkler pipe sizing"""
    errors = []
    warnings = []
    
    max_heads = FIRE_SPRINKLER_PIPE_SIZING.get(pipe_size)
    
    if max_heads:
        if head_count > max_heads:
            errors.append(f"NFPA 13: {pipe_size}\" pipe too small for {head_count} heads (max {max_heads} per pipe schedule)")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def compare_wire_size(size1, size2):
    """Compare wire sizes: returns -1 if size1 < size2, 0 if equal, 1 if size1 > size2"""
    wire_order = ["14", "12", "10", "8", "6", "4", "3", "2", "1", 
                  "1/0", "2/0", "3/0", "4/0",
                  "250", "300", "350", "400", "500", "600", "750", "1000"]
    try:
        idx1 = wire_order.index(size1)
        idx2 = wire_order.index(size2)
        if idx1 < idx2:
            return -1
        elif idx1 > idx2:
            return 1
        return 0
    except ValueError:
        return None  # Unknown size
