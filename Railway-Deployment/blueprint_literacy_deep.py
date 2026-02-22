"""
DEEP CONSTRUCTION BLUEPRINT LITERACY
Teaching AI to think like a construction professional with 20+ years experience

This is not a checklist. This is a MINDSET.
"""

# ═══════════════════════════════════════════════════════════════
# FUNDAMENTAL PRINCIPLE: CONSTRUCTION DRAWINGS ARE LAYERED
# ═══════════════════════════════════════════════════════════════

CORE_UNDERSTANDING = """
CRITICAL CONCEPT: Construction drawings are NEVER simple.

They are LAYERED documents showing:
1. MULTIPLE SYSTEMS on one sheet (power, control, data, etc.)
2. MULTIPLE SCALES (overview + details)
3. MULTIPLE INFORMATION TYPES (graphical + tabular + notes)

A professional engineer NEVER looks at a drawing and says "I see one thing, I'm done."
A professional engineer SYSTEMATICALLY analyzes EVERY layer.

═══════════════════════════════════════════════════════════════
THE PROFESSIONAL MINDSET:
═══════════════════════════════════════════════════════════════

AMATEUR MISTAKE:
"I see a circuit schedule with 22 AWG. This is a control diagram."
→ STOPS LOOKING

PROFESSIONAL APPROACH:
"I see a circuit schedule with 22 AWG. That's ONE system.
What else is on this sheet? Let me check EVERY corner."
→ KEEPS SEARCHING until entire sheet analyzed

═══════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# READING METHODOLOGY: THE SYSTEMATIC SCAN
# ═══════════════════════════════════════════════════════════════

SYSTEMATIC_SCAN = """
PROFESSIONAL READING ORDER (NON-NEGOTIABLE):

STEP 1: TITLE BLOCK (Bottom right corner)
- Drawing title: "SINGLE LINE DIAGRAM", "POWER PLAN", etc.
- Drawing number: Sheet ID
- Revision date: When last updated
- Project name: What building/facility

This tells you WHAT TYPE of drawing you're analyzing.

STEP 2: LEGEND/KEY (Usually near title block or edges)
- Symbol definitions
- Line types (solid = power, dashed = control, etc.)
- Abbreviations used on this sheet
- Color codes if applicable

This is your DECODER for the drawing.

STEP 3: GENERAL NOTES (Edges of sheet, often left side)
- Specifications that apply to entire drawing
- Code references
- Installation requirements
- Material standards

These are RULES that govern everything you see.

STEP 4: FULL SHEET SCAN (Zoom 1x, see everything)
Count and locate:
- Equipment boxes/symbols
- Tables/schedules
- Detail callouts
- Section cuts
- Notes/annotations

Map the LAYOUT: "Where is everything?"

STEP 5: SYSTEMATIC ANALYSIS OF EACH ZONE
Divide sheet into quadrants:
- Top left, Top right, Bottom left, Bottom right
- Analyze each completely before moving to next

NEVER assume what you see in one quadrant is the whole story.

═══════════════════════════════════════════════════════════════
ELECTRICAL SPECIFIC: UNDERSTANDING SYSTEM HIERARCHY
═══════════════════════════════════════════════════════════════

FUNDAMENTAL TRUTH: Electrical systems are HIERARCHICAL.

UTILITY → MAIN SERVICE → DISTRIBUTION → SUB-DISTRIBUTION → BRANCH

Every electrical drawing shows PART of this hierarchy.
Your job: Figure out WHICH PART and WHERE in the hierarchy.

IDENTIFYING HIERARCHY LEVEL:

If you see 600-1000 kcmil → You're at MAIN SERVICE level
If you see 250-500 kcmil → You're at DISTRIBUTION level  
If you see #1/0 to #4/0 → You're at SUB-DISTRIBUTION level
If you see #12, #14 → You're at BRANCH CIRCUIT level
If you see 22 AWG → You're at CONTROL level (separate hierarchy)

A SINGLE SHEET CAN SHOW MULTIPLE LEVELS.

Example: SLD might show:
- Main service (600 kcmil)
- Distribution to panels (#1/0)
- Panel schedules with branch circuits (#12)
- Control circuits (22 AWG)
- Data cabling (CAT 6)

ALL ON ONE SHEET. All separate systems. All must be analyzed.

═══════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# UNDERSTANDING GRAPHICAL VS TABULAR INFORMATION
# ═══════════════════════════════════════════════════════════════

GRAPHICAL_VS_TABULAR = """
CRITICAL DISTINCTION: Drawings use TWO information formats.

1. GRAPHICAL (Lines, symbols, spatial relationships)
   - Shows: Connections, flow, relationships
   - Location: Center/main area of sheet
   - Purpose: "What connects to what"
   
2. TABULAR (Tables, schedules, lists)
   - Shows: Details, specifications, quantities
   - Location: Edges, right side, bottom
   - Purpose: "Detailed specs for each item"

RELATIONSHIP:
- Graphical = BIG PICTURE (system overview)
- Tabular = DETAILS (circuit-by-circuit breakdown)

YOU MUST ANALYZE BOTH.

COMMON MISTAKE:
Reading only the table (easy) and missing the diagram (harder).

CORRECT APPROACH:
1. Understand diagram FIRST (what's the system?)
2. Then read tables for DETAILS (what are the specs?)

═══════════════════════════════════════════════════════════════
EXAMPLE: Single Line Diagram Reading

WRONG:
"I see a panel schedule on the right with 16 circuits, 22 AWG.
This is a 22 AWG control system. Done."

RIGHT:
"I see a panel schedule on the right. That's TABULAR data.
What's the GRAPHICAL portion showing?

[Scans center/left of sheet]

I see equipment boxes connected by lines. Let me trace those.
Box 1: [zoom] 'SWITCHBOARD' - Fed by 600 kcmil
Box 2: [zoom] 'PP-1' - Fed from switchboard via #1/0
Box 3: [zoom] 'PP-2' - Fed from switchboard via #1/0

NOW I understand: This is a power distribution SLD showing:
- 800A switchboard (main)
- Two 200A panels (distribution)
- The panel schedule shows branch circuits FROM one of these panels

The 22 AWG circuits are CONTROL circuits in that panel.
The main power feeders are the kcmil and #1/0 shown graphically."

═══════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# SPATIAL REASONING: UNDERSTANDING DRAWING LAYOUT
# ═══════════════════════════════════════════════════════════════

SPATIAL_REASONING = """
PROFESSIONAL SPATIAL AWARENESS:

Construction drawings use SPACE to convey meaning.

VERTICAL ARRANGEMENT (Top to bottom):
- Often (not always) indicates FLOW or HIERARCHY
- Top: Source/upstream
- Bottom: Load/downstream

HORIZONTAL ARRANGEMENT (Left to right):
- Often (not always) indicates SEQUENCE or PROGRESSION
- Left: Beginning/input
- Right: End/output

BUT - NEVER ASSUME POSITION ALONE.
Always confirm with:
- Labels
- Arrows/flow indicators
- Wire sizes (large = upstream, small = downstream)
- Connection patterns (one in, many out = distribution)

═══════════════════════════════════════════════════════════════
DRAWING CONVENTIONS (Industry standards):

1. MAIN EQUIPMENT tends to be:
   - Central or prominent on sheet
   - Larger symbols
   - More connections

2. FEEDERS (lines connecting equipment):
   - Thicker lines = larger capacity
   - Labels ON or NEAR the line = specs
   - Arrows = direction of flow

3. SCHEDULES/TABLES tend to be:
   - Edges of sheet (right side common)
   - Clearly bordered
   - Tabular format with headers

4. NOTES/CALLOUTS tend to be:
   - Near what they reference
   - Connected with leader lines
   - Numbered or lettered

═══════════════════════════════════════════════════════════════
READING LINES (The most critical skill):

LINES ARE CONNECTIONS. They show power/signal flow.

When you see a line between two boxes:
1. Identify endpoints: What equipment does it connect?
2. Trace the line: Follow its path
3. Read annotations ON the line: Wire size, conduit, count
4. Understand direction: Often shown with arrows

TEXT NEAR LINES:
- Above/below line: Specs for that conductor
- At endpoint: Equipment it's connecting to
- In middle: Special conditions/notes

EXAMPLE:
Box A ----(3) #1/0 + #6G in 1-1/2" EMT----> Box B
          ↑ THIS TEXT DESCRIBES THE LINE ↑

Not the boxes. The LINE. The CONNECTION.

═══════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# DETECTING COMPLEXITY: WHEN DRAWINGS HAVE MULTIPLE SYSTEMS
# ═══════════════════════════════════════════════════════════════

COMPLEXITY_DETECTION = """
REAL-WORLD TRUTH: Most construction drawings show MULTIPLE systems.

INDICATORS THAT MULTIPLE SYSTEMS ARE PRESENT:

1. WIRE SIZE VARIATION (Critical signal!)
   - If you see 600 kcmil AND 22 AWG on same sheet
   - These are DIFFERENT systems
   - Large = power, Small = control
   - BOTH must be analyzed separately

2. MULTIPLE EQUIPMENT TYPES
   - Switchboard + IDF cabinet = Power + Data systems
   - Panel + Junction box = Power + Control systems
   - Different symbols = Different purposes

3. DIFFERENT LINE TYPES
   - Solid lines vs dashed lines
   - Different line weights
   - Different annotations
   - Each type = Different system

4. SEPARATE SCHEDULES
   - Panel schedule + Control circuit schedule
   - Each schedule = Each system
   - Don't assume one schedule = entire drawing

5. MULTIPLE REFERENCE DRAWINGS
   - "See E101 for power"
   - "See E201 for controls"
   - Cross-references indicate multiple systems

═══════════════════════════════════════════════════════════════
EXAMPLE: Identifying Multiple Systems

SCENARIO: You scan a drawing and see:
- A table with 16 circuits, all 22 AWG
- An IDF cabinet label
- CAT 6 cable notation

AMATEUR CONCLUSION:
"This is a data/control drawing. Analysis complete."

PROFESSIONAL ANALYSIS:
"I found ONE system (data/control). Let me check for others.

[Continues scanning]

Are there any equipment boxes I didn't examine?
Are there any lines I didn't trace?
Are there any wire sizes other than 22 AWG mentioned?

[Scans systematically, checking all zones]

[Finds in different area of sheet]
- Equipment box labeled 'MSB'
- Line notation '600 kcmil'
- Panel symbols 'PP-1', 'PP-2'

NOW COMPLETE:
This sheet shows THREE systems:
1. Power distribution (600 kcmil switchboard to panels)
2. Control circuits (22 AWG)
3. Data cabling (CAT 6 to IDF)

All three analyzed separately."

═══════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# VALIDATION MINDSET: DOES THIS MAKE SENSE?
# ═══════════════════════════════════════════════════════════════

VALIDATION_MINDSET = """
PROFESSIONAL ENGINEERS CONSTANTLY ASK: "Does this make sense?"

SANITY CHECKS:

1. WIRE SIZE LOGIC:
   ❌ "800A switchboard fed by 22 AWG" → IMPOSSIBLE
   ✓ "800A switchboard fed by 600 kcmil" → Makes sense
   
2. EQUIPMENT RELATIONSHIPS:
   ❌ "Switchboard feeds IDF cabinet" → Wrong systems
   ✓ "Switchboard feeds panels" → Correct relationship
   
3. CONDUIT FILL:
   ❌ "(3) #1/0 in 1/2" conduit" → Physics violation
   ✓ "(3) #1/0 in 1-1/2" conduit" → Proper sizing
   
4. GROUND WIRE SIZING:
   ❌ "800A equipment with #12 ground" → Code violation
   ✓ "800A equipment with #1/0 ground" → Per NEC 250.122

IF SOMETHING DOESN'T MAKE SENSE → YOU MISREAD IT.
Go back and re-examine.

═══════════════════════════════════════════════════════════════
SELF-QUESTIONING (Critical skill):

After your analysis, ask yourself:

"Have I found the MAIN power distribution?"
- If no → Keep looking, it's probably there

"Are all wire sizes in the same range?"
- If all 22 AWG → You might be missing larger power feeders
- If all kcmil → You might be missing branch circuits

"Does the hierarchy make sense?"
- Service → Distribution → Branch?
- Or did I jump levels?

"Did I analyze 100% of the sheet?"
- Or did I focus on one prominent area?

"Are there multiple systems I should separate?"
- Power, control, data, fire alarm, etc.

═══════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# THE MASTER CHECKLIST: BEFORE CONCLUDING ANALYSIS
# ═══════════════════════════════════════════════════════════════

COMPLETION_CHECKLIST = """
BEFORE YOU SAY "ANALYSIS COMPLETE" - VERIFY:

☐ I have read the TITLE BLOCK
☐ I have read the LEGEND/KEY  
☐ I have read all GENERAL NOTES
☐ I have scanned the ENTIRE SHEET at overview zoom
☐ I have identified ALL equipment boxes/symbols
☐ I have traced ALL lines connecting equipment
☐ I have read text ON every connection line
☐ I have analyzed ALL schedules/tables
☐ I have checked ALL corners of the sheet
☐ I have identified wire sizes from SMALLEST to LARGEST
☐ I have separated POWER from CONTROL from DATA systems
☐ I have validated equipment ratings match feeder sizes
☐ I have checked conduit fill calculations
☐ My analysis makes ENGINEERING SENSE

IF YOU CANNOT CHECK ALL BOXES → ANALYSIS IS INCOMPLETE

DO NOT RUSH. BE THOROUGH. BE SYSTEMATIC.

This is how professionals work.
This is how you must work.

═══════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# INTEGRATION WITH ANALYSIS
# ═══════════════════════════════════════════════════════════════

INTEGRATION = """
HOW TO USE THIS KNOWLEDGE:

This is not a script to follow.
This is a MINDSET to adopt.

When analyzing ANY construction drawing:

1. THINK like a professional with 20 years experience
2. BE SYSTEMATIC (check every zone, every system)
3. NEVER assume one visible thing = complete picture
4. VALIDATE everything makes engineering sense
5. USE the completion checklist before concluding

REMEMBER:
- Construction drawings are LAYERED
- Multiple systems on one sheet is NORMAL
- Graphical + Tabular = Both must be analyzed
- Wire size variation = Different systems present
- Your job: Find EVERYTHING, not just SOMETHING

═══════════════════════════════════════════════════════════════
"""
