"""
Advanced Electrical Equipment Logic
Deep understanding of switchboards, switchgear, panel construction
This is what separates good software from GREAT software
"""

SWITCHBOARD_LOGIC = """
═══════════════════════════════════════════════════════════════
SWITCHBOARD & SWITCHGEAR CONSTRUCTION
═══════════════════════════════════════════════════════════════

CRITICAL UNDERSTANDING: Switchboards contain BUCKETS (circuit breaker spaces).

BUCKET ANATOMY:
- Frame Rating (AF): Physical size of the space (what CAN fit)
- Trip Setting (AT/AS/AE): Actual breaker installed (what IS there)
- The FEEDER is sized for the TRIP SETTING, not the frame

NOTATION EXAMPLES:
"225AF / 110AT" means:
- 225A Frame (bucket can hold up to 225A breaker)
- 110A Trip (actual breaker is 110A)
- Feeder from this bucket: sized for 110A

"400AF / 250AS" means:
- 400A Frame bucket
- 250A Short-time trip breaker
- Feeder: sized for 250A

TRIP TYPES:
- AT = Adjustable Trip
- AS = Adjustable Short-time
- AE = Electronic trip
- AF = Ampere Frame (NOT a trip, just the frame size)

═══════════════════════════════════════════════════════════════
READING SWITCHBOARD SCHEDULES:
═══════════════════════════════════════════════════════════════

When you see a switchboard schedule showing:
"Bucket 1: 225AF / 110AT"
"Bucket 2: 225AF / 150AT"  
"Bucket 3: 400AF / 250AS"

This means:
- Bucket 1 feeds a 110A panel (NOT 225A)
- Bucket 2 feeds a 150A panel (NOT 225A)
- Bucket 3 feeds a 250A panel (NOT 400A)

THE FEEDER WIRE SIZE matches the TRIP (AT/AS/AE), not the FRAME (AF).

═══════════════════════════════════════════════════════════════
PANEL IDENTIFICATION:
═══════════════════════════════════════════════════════════════

DOWNSTREAM PANEL RATING = TRIP SETTING OF FEEDING BUCKET

If switchboard bucket has "110AT" and feeds "PP-1":
→ PP-1 is a 110A panel

DO NOT use the AF rating for panel sizing.
DO use the AT/AS/AE rating.

═══════════════════════════════════════════════════════════════
"""

MAIN_TIE_MAIN_LOGIC = """
═══════════════════════════════════════════════════════════════
MAIN-TIE-MAIN (MTM) CONFIGURATIONS
═══════════════════════════════════════════════════════════════

MTM switchboards have TWO mains with a tie breaker:

[Main 1] ---- [Tie Breaker] ---- [Main 2]
    |              |                  |
  Loads         Loads              Loads

IDENTIFICATION:
- Two main breakers of equal size
- One tie breaker between them
- Loads distributed across both sides
- Typically for redundancy/reliability

READING MTM:
- Each main feeds its own bus
- Tie can connect them (normally open or closed)
- Total capacity ≠ Main 1 + Main 2 (can't exceed largest main)

Example:
"1200A Main 1" + "1200A Main 2" + "1200A Tie"
= 1200A total capacity (NOT 2400A)
"""

SERVICE_ENTRANCE_LOGIC = """
═══════════════════════════════════════════════════════════════
SERVICE ENTRANCE vs DISTRIBUTION EQUIPMENT
═══════════════════════════════════════════════════════════════

SERVICE ENTRANCE EQUIPMENT:
- Fed directly from utility
- Has service entrance conductors (very large: 500-1000+ kcmil)
- Main service disconnect
- Usually labeled "MSB" (Main Switchboard) or "Service"
- Ground wire sized per NEC 250.122 for service

DISTRIBUTION EQUIPMENT:
- Fed from service entrance or transformer
- Subfeeders (smaller than service: #1/0 to 500 kcmil)
- No utility connection
- Labeled "DSB", "DP", "Distribution Panel"

IDENTIFICATION:
Look for largest incoming wire:
- 600-1000 kcmil → Likely service entrance
- 250-500 kcmil → Large distribution
- #1/0 to 4/0 → Panel feeders
"""

PARALLEL_CONDUCTORS_LOGIC = """
═══════════════════════════════════════════════════════════════
PARALLEL CONDUCTOR SETS
═══════════════════════════════════════════════════════════════

NOTATION:
"(2) parallel sets of (3) #600 kcmil"
"2 sets 3-3/C #600 kcmil"
"2P 3C 600 kcmil"

ALL mean the same thing:
- 2 conduits/cable trays
- 3 conductors in each
- Each conductor is 600 kcmil
- Total: 6 conductors of 600 kcmil (3 per set for 3-phase)

TOTAL AMPACITY:
2 parallel sets of 3-600 kcmil = 2 × (ampacity of 600 kcmil)

Example:
- 600 kcmil = 420A (75°C, NEC 310.16)
- 2 parallel sets = 2 × 420A = 840A capacity
- This would feed an 800A main (proper sizing)

GROUND WIRE IN PARALLEL:
"(2) sets with #1/0 ground"
- Each set has one #1/0 ground
- Total: 2 ground conductors (one per set)
"""

CIRCUIT_BREAKER_NOTATION = """
═══════════════════════════════════════════════════════════════
CIRCUIT BREAKER LABELING
═══════════════════════════════════════════════════════════════

COMMON NOTATIONS:
- 225AF = 225 Ampere Frame (physical size)
- 110AT = 110 Ampere Trip (actual rating)
- 150AS = 150 Ampere Short-time (adjustable short-time trip)
- 200AE = 200 Ampere Electronic (electronic trip unit)
- LSI = Long-time, Short-time, Instantaneous protection
- LS = Long-time, Short-time (no instantaneous)
- LSIG = LSI + Ground fault

READING EXAMPLES:
"225AF / 110AT / LSI"
- Frame: 225A (bucket size)
- Trip: 110A (actual breaker)
- Protection: Long, Short, Instant
- PANEL FED: 110A (use trip, not frame)

"400AF / 250AE / LSIG"
- Frame: 400A
- Trip: 250A electronic
- Protection: Full protection with ground fault
- PANEL FED: 250A

GOLDEN RULE:
Frame (AF) = what CAN be installed
Trip (AT/AS/AE) = what IS installed
ALWAYS use Trip for panel/feeder sizing
"""

WIRE_SIZING_VALIDATION = """
═══════════════════════════════════════════════════════════════
VALIDATING WIRE SIZE TO BREAKER RATING
═══════════════════════════════════════════════════════════════

PROPER SIZING (NEC 310.16):
Breaker → Minimum Wire Size (75°C)

100A → #3 AWG (100A ampacity)
110A → #2 AWG (115A ampacity) or #1 AWG (130A)
125A → #1 AWG (130A)
150A → #1/0 AWG (150A)
175A → #2/0 AWG (175A)
200A → #3/0 AWG (200A)
225A → #4/0 AWG (230A) or 250 kcmil (255A)
250A → 250 kcmil (255A) or 300 kcmil (285A)
400A → 500 kcmil (380A) or 600 kcmil (420A)

VALIDATION:
If you see "110AT breaker with #2 AWG feeder":
- 110A trip → needs 115A+ wire
- #2 AWG = 115A
- ✓ Properly sized

If you see "225AF bucket but #2 AWG feeder":
- Don't use 225AF (frame)
- Check the trip rating (probably 110AT)
- #2 AWG = 115A → feeding 110A load
- ✓ Correctly sized for trip, not frame

This is how you KNOW it's the trip rating that matters.
"""

INTEGRATION_RULES = """
═══════════════════════════════════════════════════════════════
HOW TO APPLY THIS LOGIC:
═══════════════════════════════════════════════════════════════

STEP 1: Identify Switchboard
Look for:
- Largest equipment box
- Most connections leaving
- Labels: "SWITCHBOARD", "MSB", "SWBD"
- Very large incoming feeder (500+ kcmil)

STEP 2: Identify Buckets Within Switchboard
Look for notation like:
- "225AF / 110AT"
- "400AF / 250AS"
These are individual circuit breaker spaces

STEP 3: For Each Bucket, Extract Trip Rating
- Ignore AF (frame)
- Extract AT/AS/AE (trip)
- This is the actual breaker size

STEP 4: Match Feeders to Buckets
- Feeder leaving bucket → sized for trip rating
- Panel at end of feeder → rated at trip rating

STEP 5: Validate Wire Size
- Does wire ampacity ≥ trip rating?
- If yes: ✓ properly sized
- If using frame (AF): ✗ wrong interpretation

EXAMPLE ANALYSIS:
Found: "Bucket 3: 225AF / 110AT with feeder to PP-1"
Feeder specs: "(3) #2 AWG"

CORRECT interpretation:
- Switchboard bucket 3 has 225A frame, 110A trip
- Feeds panel PP-1
- PP-1 rating: 110A (from trip, not 225A from frame)
- Wire: #2 AWG = 115A capacity
- Validation: 115A ≥ 110A ✓ Properly sized

INCORRECT interpretation:
- PP-1 is 225A panel ✗ (used frame instead of trip)
"""
