"""
COMPLETE MULTI-TRADE EQUIPMENT LOGIC
HVAC, Plumbing, Fire Protection - Deep understanding
"""

# ═══════════════════════════════════════════════════════════════
# HVAC / MECHANICAL EQUIPMENT LOGIC
# ═══════════════════════════════════════════════════════════════

HVAC_EQUIPMENT_LOGIC = """
═══════════════════════════════════════════════════════════════
AIR HANDLING UNITS (AHU)
═══════════════════════════════════════════════════════════════

IDENTIFICATION:
- Label: "AHU", "AIR HANDLER", "AHU-1"
- CFM rating (airflow)
- Supply and return duct connections

SIZING:
Rated in CFM (cubic feet per minute)
Rule of thumb: 400 CFM per ton of cooling
Example: 2000 CFM AHU = ~5 ton capacity

COMPONENTS SHOWN:
- Supply fan
- Return fan (if present)
- Heating coil
- Cooling coil
- Filters
- Dampers

DUCT CONNECTIONS:
Supply duct: Distributes conditioned air
Return duct: Returns air to unit
Outside air duct: Fresh air intake
Exhaust duct: Exhausts stale air

NOTATION EXAMPLES:
"AHU-1: 5000 CFM, Supply/Return"
"Air Handler #2: 3500 CFM with HW coil"
"""

ROOFTOP_UNIT_LOGIC = """
═══════════════════════════════════════════════════════════════
ROOFTOP UNITS (RTU)
═══════════════════════════════════════════════════════════════

IDENTIFICATION:
- Label: "RTU", "PACKAGE UNIT", "RTU-1"
- Tonnage rating
- All-in-one: heating, cooling, fan

SIZING:
Rated in TONS (of cooling)
Common sizes: 3, 5, 7.5, 10, 12.5, 15, 20, 25, 30 tons

CFM CAPACITY:
CFM = Tons × 400 (standard)
Example: 10 ton RTU = ~4000 CFM

DUCT CONNECTIONS:
Supply duct: Conditioned air to space
Return duct: Air back from space
(No separate heating/cooling units - all integrated)

GAS INPUT (if gas heating):
MBH (1000 BTU/hr) or BTU/hr
Example: "RTU-3: 10 TON, 200 MBH gas input"
"""

CHILLER_LOGIC = """
═══════════════════════════════════════════════════════════════
CHILLERS (Central Plant)
═══════════════════════════════════════════════════════════════

PURPOSE: Produce chilled water for building cooling

SIZING:
Rated in TONS (refrigeration tons)
Large chillers: 100, 200, 300, 500, 1000+ tons

TYPES:
- Air-cooled: Reject heat to outdoor air
- Water-cooled: Reject heat to cooling tower

PIPING CONNECTIONS:
CHWS = Chilled Water Supply (to building)
CHWR = Chilled Water Return (from building)
CWS = Condenser Water Supply (to cooling tower)
CWR = Condenser Water Return (from cooling tower)

PIPE SIZING:
Based on flow rate (GPM) and head loss
Typical: 2.4 GPM per ton
Example: 500 ton chiller = ~1200 GPM flow

NOTATION:
"CH-1: 400 TON water-cooled chiller"
"CHWS/CHWR: 8" pipe"
"""

BOILER_LOGIC = """
═══════════════════════════════════════════════════════════════
BOILERS (Heating Plant)
═══════════════════════════════════════════════════════════════

PURPOSE: Produce hot water or steam for heating

SIZING:
Rated in MBH or BTU/hr output
Common: 500 MBH, 1000 MBH, 2000 MBH, 5000 MBH

INPUT vs OUTPUT:
Input: Fuel consumption (MBH input)
Output: Heat delivered (MBH output)
Efficiency: Output/Input (usually 80-95%)

PIPING:
HWS = Hot Water Supply (to building)
HWR = Hot Water Return (from building)
For steam: Supply and condensate return

FUEL TYPES:
- Natural gas (most common)
- #2 Oil
- Electric (resistance or heat pump)

NOTATION:
"B-1: 2000 MBH gas-fired boiler"
"HWS/HWR: 4" pipe, 180°F supply"
"""

DUCTWORK_SIZING_LOGIC = """
═══════════════════════════════════════════════════════════════
DUCT SIZING & NOTATION
═══════════════════════════════════════════════════════════════

RECTANGULAR DUCT:
Notation: Width × Height
Example: "24×12" = 24" wide, 12" high

SIZING TABLES (at 0.1" friction loss):
12×8 → 200 CFM max
16×10 → 320 CFM
20×12 → 500 CFM
24×16 → 900 CFM
30×20 → 1500 CFM

ROUND DUCT:
Notation: Diameter with Ø
Example: "16Ø" = 16" diameter

VELOCITY LIMITS:
Supply duct: 600-1200 FPM (feet per minute)
Return duct: 500-800 FPM
Main trunks: 1200-1800 FPM
High velocity: >2000 FPM (noise risk)

VALIDATION:
CFM / (Duct Area in sq ft) = Velocity (FPM)
If velocity >2000 FPM: Oversized, potential noise
If velocity <600 FPM: Undersized, poor distribution
"""

VAV_SYSTEM_LOGIC = """
═══════════════════════════════════════════════════════════════
VARIABLE AIR VOLUME (VAV) SYSTEMS
═══════════════════════════════════════════════════════════════

COMPONENTS:
VAV boxes: Control airflow to zones
Located on branch ducts from main

NOTATION:
"VAV-1: 500-1500 CFM with reheat"
Min CFM = 500 (minimum airflow)
Max CFM = 1500 (maximum airflow)
Reheat = electric or hot water coil

SYSTEM LAYOUT:
AHU → Main duct → VAV boxes → Zone ductwork

DUCT SIZING:
Main duct: Sized for sum of VAV max CFM
Branch to VAV: Sized for that VAV max CFM
"""

# ═══════════════════════════════════════════════════════════════
# PLUMBING EQUIPMENT LOGIC
# ═══════════════════════════════════════════════════════════════

PLUMBING_SYSTEM_LOGIC = """
═══════════════════════════════════════════════════════════════
DOMESTIC WATER SYSTEMS
═══════════════════════════════════════════════════════════════

PIPE SIZING - WATER SUPPLY:
Based on FIXTURE UNITS (WSFU)

Fixture Unit Values:
- Water closet (tank): 3 WSFU
- Lavatory: 1 WSFU
- Shower: 2 WSFU
- Kitchen sink: 1.5 WSFU
- Bathtub: 2 WSFU
- Dishwasher: 1.5 WSFU
- Washing machine: 2 WSFU

Pipe Size for WSFU (UPC):
1/2" → 3 WSFU max
3/4" → 6 WSFU
1" → 12 WSFU
1-1/4" → 20 WSFU
1-1/2" → 27 WSFU
2" → 44 WSFU
2-1/2" → 72 WSFU
3" → 108 WSFU

NOTATION:
"CW" = Cold Water
"HW" = Hot Water
"HWR" = Hot Water Recirculation
"DWV" = Drain-Waste-Vent

WATER SERVICE:
Main incoming: Usually 2" to 4"
Based on total fixture units in building
"""

DRAIN_SYSTEM_LOGIC = """
═══════════════════════════════════════════════════════════════
SANITARY DRAINAGE SYSTEMS
═══════════════════════════════════════════════════════════════

PIPE SIZING - DRAINS:
Based on DRAINAGE FIXTURE UNITS (DFU)

DFU Values:
- Water closet: 3-6 DFU (depends on flush type)
- Lavatory: 1 DFU
- Shower: 2 DFU
- Kitchen sink: 2 DFU
- Floor drain: 1-3 DFU
- Bathtub: 2 DFU

Pipe Size for DFU (horizontal):
1-1/2" → 3 DFU max
2" → 6 DFU
3" → 20 DFU (building drain: 42 DFU)
4" → 160 DFU (building drain: 216 DFU)
6" → 620 DFU (building drain: 840 DFU)

SLOPE REQUIREMENTS:
2" and smaller: 1/4" per foot minimum
3"-6": 1/8" per foot minimum
8" and larger: 1/16" per foot minimum

VENTING:
Every fixture needs vent
Vent sizes based on developed length and DFU
Common: 1-1/2" to 3" vents
"""

WATER_HEATER_LOGIC = """
═══════════════════════════════════════════════════════════════
WATER HEATERS
═══════════════════════════════════════════════════════════════

SIZING:
Capacity: Gallons (storage)
Recovery: GPH (gallons per hour)
Input: BTU/hr or kW

TYPES:
Tank: 30, 40, 50, 75, 100, 120 gallons
Tankless: Rated in GPM at temperature rise
Commercial: 100-500+ gallons

NOTATION:
"WH-1: 75 gal, 75 MBH input, gas"
"Tankless WH: 8 GPM at 70°F rise"

CONNECTIONS:
CW = Cold water inlet
HW = Hot water outlet
Relief valve
Gas or electric supply
"""

# ═══════════════════════════════════════════════════════════════
# FIRE PROTECTION SYSTEMS
# ═══════════════════════════════════════════════════════════════

FIRE_SPRINKLER_LOGIC = """
═══════════════════════════════════════════════════════════════
FIRE SPRINKLER SYSTEMS (NFPA 13)
═══════════════════════════════════════════════════════════════

HAZARD CLASSIFICATIONS:
Light Hazard:
- Occupancy: Offices, churches, schools
- Density: 0.10 gpm/sq ft
- Max coverage: 200 sq ft per head
- Max spacing: 15 ft

Ordinary Hazard Group 1:
- Occupancy: Parking, restaurants
- Density: 0.15 gpm/sq ft
- Max coverage: 130 sq ft per head
- Max spacing: 15 ft

Ordinary Hazard Group 2:
- Occupancy: Manufacturing, warehouses
- Density: 0.20 gpm/sq ft
- Max coverage: 130 sq ft per head

Extra Hazard:
- Occupancy: High hazard manufacturing
- Density: 0.30-0.40 gpm/sq ft
- Max coverage: 100 sq ft per head
- Max spacing: 12 ft

PIPE SCHEDULE (NFPA 13):
Number of heads per pipe size:
1" → 2 heads max
1-1/4" → 3 heads
1-1/2" → 5 heads
2" → 10 heads
2-1/2" → 20 heads
3" → 40 heads
4" → 100 heads
5" → 160 heads
6" → 275 heads

HYDRAULIC CALCULATION:
Alternative to pipe schedule
Based on actual flow and pressure requirements
More efficient pipe sizing
"""

FIRE_PUMP_LOGIC = """
═══════════════════════════════════════════════════════════════
FIRE PUMPS (NFPA 20)
═══════════════════════════════════════════════════════════════

PURPOSE: Boost water pressure for sprinkler system

SIZING:
Rated in GPM and PSI
Common: 500 GPM at 75 PSI
        750 GPM at 100 PSI
        1000 GPM at 125 PSI

COMPONENTS:
- Fire pump (centrifugal)
- Jockey pump (maintain pressure)
- Controller
- Suction from water main or tank
- Discharge to sprinkler system

ELECTRICAL:
Requires dedicated feeder
Sized for locked rotor amps (LRA)
Typical: 200-600A depending on HP

NOTATION:
"FP-1: 750 GPM @ 100 PSI, 100 HP"
"Fire pump with 480V/3ph/100HP motor"
"""

FIRE_ALARM_SYSTEM_LOGIC = """
═══════════════════════════════════════════════════════════════
FIRE ALARM SYSTEMS (NFPA 72)
═══════════════════════════════════════════════════════════════

COMPONENTS:
FACP = Fire Alarm Control Panel (main brain)
Initiating devices: Smoke detectors, heat detectors, pull stations
Notification devices: Horns, strobes, speakers

CIRCUITS:
Initiating Device Circuits (IDC): Connect detectors
Notification Appliance Circuits (NAC): Connect horns/strobes
Signaling Line Circuits (SLC): Addressable devices

WIRE SIZING:
18 AWG: Short runs (<100 ft)
16 AWG: Medium runs (100-300 ft)
14 AWG: Long runs (>300 ft)
12 AWG: Very long or high-power NAC

SUPERVISION:
End-of-Line (EOL) resistors
Circuit monitoring for opens/shorts
Battery backup required (24-72 hours)

NOTATION:
"FACP: 10 zones, 20 IDC, 5 NAC"
"Smoke detector on IDC-3"
"Horn/strobe on NAC-1"
"""
