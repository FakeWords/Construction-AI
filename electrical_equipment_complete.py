"""
COMPLETE ELECTRICAL EQUIPMENT LOGIC
Every type of electrical equipment and configuration
This makes the agent smarter than most junior engineers
"""

TRANSFORMER_LOGIC = """
═══════════════════════════════════════════════════════════════
TRANSFORMER IDENTIFICATION & SIZING
═══════════════════════════════════════════════════════════════

TRANSFORMER NOTATION:
"75 kVA, 480V Δ - 208Y/120V"

Breakdown:
- 75 kVA = Capacity (power rating)
- 480V Δ = Primary voltage (Delta connected)
- 208Y/120V = Secondary voltage (Wye connected)
  * 208V = Line-to-line
  * 120V = Line-to-neutral

COMMON SIZES:
- 15, 30, 45, 75, 112.5, 150, 225, 300, 500, 750, 1000, 1500, 2000 kVA

VOLTAGE CONVERSIONS:
Primary → Secondary:
- 480V → 208Y/120V (most common)
- 480V → 480Y/277V (lighting)
- 4160V → 480V (medium voltage)
- 13.8kV → 480V (utility service)

AMPERAGE CALCULATION:
Secondary amps = (kVA × 1000) / (Voltage × √3)

Example: 75 kVA, 208V secondary
= (75 × 1000) / (208 × 1.732)
= 75,000 / 360
= 208A secondary

PRIMARY SIZING:
Primary conductors sized for transformer input
Secondary conductors sized for transformer output + loads

SYMBOLS TO LOOK FOR:
- Circle with coils drawn
- "XFMR", "TRANS", "T-1", "TR"
- kVA rating
- Primary/secondary voltage notation

DOWNSTREAM FROM TRANSFORMER:
What feeds from transformer secondary?
- Usually a distribution panel or switchboard
- Rated at transformer secondary amperage
- Example: 75 kVA transformer → ~200A panel downstream
"""

SUBSTATION_LOGIC = """
═══════════════════════════════════════════════════════════════
ELECTRICAL SUBSTATIONS
═══════════════════════════════════════════════════════════════

SUBSTATION COMPONENTS:
1. Primary disconnect (utility side)
2. Main transformer(s)
3. Primary metering
4. Secondary switchgear/switchboard
5. Distribution feeders

TYPICAL CONFIGURATIONS:
"Unit Substation": Transformer + switchgear in one assembly
- Common: 1000-2500 kVA
- Medium voltage primary (4160V, 13.8kV)
- Low voltage secondary (480V)

IDENTIFICATION:
- Very large kVA ratings (500+ kVA)
- Medium voltage primary (>600V)
- Multiple large feeders leaving secondary
- Labels: "SUBSTATION", "UNIT SUB", "MAIN TRANSFORMER"

PRIMARY PROTECTION:
- Primary fuses (often 100E, 200E ratings)
- Primary disconnect switch
- Lightning arrestors

SECONDARY DISTRIBUTION:
- Main secondary breaker or bus
- Multiple distribution breakers
- Typical: 1600A-4000A bus

WIRE SIZING:
Primary side:
- Medium voltage cable (often 15kV class)
- Smaller wire (less current at high voltage)

Secondary side:
- Large parallel sets common (500-1000 kcmil)
- Multiple feeders to building distribution
"""

PANEL_TYPES_LOGIC = """
═══════════════════════════════════════════════════════════════
PANEL TYPES & IDENTIFICATION
═══════════════════════════════════════════════════════════════

PANELBOARD TYPES:

**LIGHTING PANELS (LP):**
- Designation: LP-1, LP-2, etc.
- Voltage: 120/208V or 277/480V
- Circuits: Mostly lighting loads
- Breakers: Typically 15A, 20A, 30A
- Use: Lighting, small power

**RECEPTACLE PANELS (RP):**
- Designation: RP-1, RP-2, etc.
- Voltage: 120/208V
- Circuits: Receptacle/convenience outlets
- Breakers: 15A, 20A (occasionally 30A)
- Use: General power, computers, small equipment

**POWER PANELS (PP):**
- Designation: PP-1, PP-2, etc.
- Voltage: 120/208V or 480V
- Circuits: Mixed loads (power equipment)
- Breakers: Wide range (20A to 100A+)
- Use: Motors, HVAC, elevators, large equipment

**DISTRIBUTION PANELS (DP/MDP):**
- Designation: DP-1, MDP
- Usually larger (225A-600A)
- Feeds other panels
- Sub-distribution function

**EQUIPMENT PANELS:**
- Specific equipment (elevator, fire pump, etc.)
- Labeled by equipment served
- Dedicated circuits

PANEL MAIN BREAKER:
Panels have main breaker = panel rating
"200A MLO" = Main Lug Only (no main breaker, fed from upstream protection)
"200A MB" = Main Breaker (has integral main)

FEEDER TO PANEL:
Sized for panel main breaker rating
Example: 200A panel → needs wire rated 200A+
"""

SWITCHGEAR_LOGIC = """
═══════════════════════════════════════════════════════════════
SWITCHGEAR vs SWITCHBOARD
═══════════════════════════════════════════════════════════════

SWITCHGEAR:
- Ratings: 1000A-5000A+
- Construction: Metal-clad, draw-out breakers
- Voltage: Can handle medium voltage (5kV-15kV)
- Application: Main service, large distribution
- Cost: More expensive, more robust
- Labels: "SWGR", "SWITCHGEAR", "MSG"

SWITCHBOARD:
- Ratings: 400A-4000A
- Construction: Dead-front, bolt-on breakers
- Voltage: Low voltage only (600V max)
- Application: Service entrance, distribution
- Cost: Less expensive than switchgear
- Labels: "SWBD", "SB", "SWITCHBOARD"

VISUAL DIFFERENCES:
Switchgear: Larger, more compartmentalized
Switchboard: Flatter, vertical sections

BOTH can have:
- Multiple sections
- Main breaker or main lugs
- Distribution breakers in buckets
- Bus ties between sections
"""

AUTOMATIC_TRANSFER_SWITCH_LOGIC = """
═══════════════════════════════════════════════════════════════
AUTOMATIC TRANSFER SWITCHES (ATS)
═══════════════════════════════════════════════════════════════

PURPOSE: Switch between two power sources
- Normal source (utility)
- Emergency source (generator)

IDENTIFICATION:
- Two incoming feeders (normal + emergency)
- One outgoing feeder (to loads)
- Label: "ATS", "AUTOMATIC TRANSFER SWITCH"
- Rating: Amperage (100A-4000A)

OPERATION:
Normal condition: Loads fed from utility
Power failure: Automatic switch to generator
Power restored: Automatic or manual return to utility

TYPES:
- Service entrance rated (can be first disconnect)
- Distribution rated (downstream from main)

NOTATION:
"400A ATS"
- Normal: Fed from utility switchboard
- Emergency: Fed from generator
- Load: Feeds critical distribution

WIRE SIZING:
Two incoming feeders:
- Normal source: Sized for full load
- Emergency source: Sized for generator output
One outgoing feeder:
- Sized for ATS rating
"""

GENERATOR_LOGIC = """
═══════════════════════════════════════════════════════════════
EMERGENCY/STANDBY GENERATORS
═══════════════════════════════════════════════════════════════

SIZING:
Rated in kW (kilowatts)
Common sizes: 100kW, 150kW, 200kW, 250kW, 350kW, 500kW, 1000kW+

OUTPUT:
Usually 480V, 3-phase
Amperage = (kW × 1000) / (480 × 1.732 × PF)
PF = power factor (usually 0.8)

Example: 200kW generator
= (200 × 1000) / (480 × 1.732 × 0.8)
= 200,000 / 665
= ~300A output

FEEDERS FROM GENERATOR:
Sized for generator output current
Usually feeds ATS or emergency switchboard

IDENTIFICATION:
- Labels: "GEN", "GENERATOR", "STANDBY GEN"
- kW rating
- Voltage output
- Fuel type (diesel, natural gas)

SYSTEM CONFIGURATION:
Generator → ATS → Critical loads
Generator → Emergency switchboard → Critical panels
"""

BUS_DUCT_LOGIC = """
═══════════════════════════════════════════════════════════════
BUS DUCT / BUSWAY SYSTEMS
═══════════════════════════════════════════════════════════════

PURPOSE: Alternative to conduit for large feeders
Pre-fabricated metal enclosure with bus bars

RATINGS:
Common: 400A, 600A, 800A, 1000A, 1200A, 1600A, 2000A+

TYPES:
- Feeder busway (distribution)
- Plug-in busway (with tap-off points)
- Lighting busway (for lighting fixtures)

NOTATION:
"1600A Bus Duct"
"BD-1600" 
"Busway 1200A"

AMPACITY:
Bus duct rated at full ampacity
No derating like conductors
Example: 1600A bus duct can carry 1600A continuously

ADVANTAGES:
- Higher ampacity than wire in conduit
- Easier modifications
- Better for long horizontal runs

FEEDERS:
Bus duct IS the feeder (replaces wire + conduit)
"Fed by 1600A bus duct" = 1600A capacity feeder
"""

MOTOR_CONTROL_CENTER_LOGIC = """
═══════════════════════════════════════════════════════════════
MOTOR CONTROL CENTERS (MCC)
═══════════════════════════════════════════════════════════════

PURPOSE: Centralized motor control for multiple motors

STRUCTURE:
- Main incoming feeder
- Multiple compartments (buckets)
- Each compartment: motor starter for one motor
- Sizes: Based on largest motor + total load

IDENTIFICATION:
- Label: "MCC", "MOTOR CONTROL CENTER"
- Multiple small feeders leaving (to motors)
- Each compartment labeled with motor number

COMPARTMENT NOTATION:
"MCC-1-3" = MCC #1, Compartment #3
"Starter Size: NEMA 2"
"Motor: 25 HP, 480V"

FEEDER TO MCC:
Sized for: 125% of largest motor + 100% of all others
NEC 430.24

OUTGOING CIRCUITS:
Each motor has:
- Motor starter
- Overload protection
- Disconnect
- Control circuit
"""
