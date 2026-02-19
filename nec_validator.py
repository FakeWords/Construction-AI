"""
NEC Code Compliance Module
Electrical code validation and reference system
"""

from typing import List, Dict, Optional
from enum import Enum


class NECVersion(str, Enum):
    NEC_2017 = "2017"
    NEC_2020 = "2020"
    NEC_2023 = "2023"


class CodeViolation:
    def __init__(self, severity: str, code_ref: str, description: str, location: str = ""):
        self.severity = severity  # "critical", "warning", "info"
        self.code_ref = code_ref  # NEC article reference
        self.description = description
        self.location = location


class NECValidator:
    """NEC code compliance checker"""
    
    def __init__(self, nec_version: NECVersion = NECVersion.NEC_2023):
        self.version = nec_version
        self.violations = []
        
        # Wire ampacity tables (simplified - NEC Table 310.16)
        self.wire_ampacity = {
            "14": 15,   # 14 AWG
            "12": 20,   # 12 AWG
            "10": 30,   # 10 AWG
            "8": 50,    # 8 AWG
            "6": 65,    # 6 AWG
            "4": 85,    # 4 AWG
            "3": 100,   # 3 AWG
            "2": 115,   # 2 AWG
            "1": 130,   # 1 AWG
            "1/0": 150, # 1/0 AWG
            "2/0": 175, # 2/0 AWG
            "3/0": 200, # 3/0 AWG
            "4/0": 230, # 4/0 AWG
        }
        
        # Conduit fill percentages (NEC Chapter 9, Table 1)
        self.conduit_fill_limits = {
            "1_wire": 53,  # 1 wire = 53% fill
            "2_wires": 31, # 2 wires = 31% fill
            "3+_wires": 40 # 3+ wires = 40% fill
        }
        
        # GFCI requirements by location (NEC 210.8)
        self.gfci_locations = [
            "bathroom", "kitchen", "outdoor", "basement", "garage", 
            "crawl space", "laundry", "utility", "wet bar", "sink"
        ]
        
        # AFCI requirements (NEC 210.12)
        self.afci_locations = [
            "bedroom", "family room", "dining room", "living room",
            "parlor", "library", "den", "sunroom", "recreation room",
            "closet", "hallway", "laundry"
        ]
    
    def check_voltage_drop(self, wire_size: str, length_feet: float, 
                          current_amps: float, voltage: int = 120) -> Optional[CodeViolation]:
        """
        Check voltage drop compliance
        NEC recommends max 3% on branch circuits, 5% total
        """
        # Resistance per 1000ft for copper wire (ohms)
        wire_resistance = {
            "14": 3.07, "12": 1.93, "10": 1.21, "8": 0.764,
            "6": 0.491, "4": 0.308, "3": 0.245, "2": 0.194,
            "1": 0.154, "1/0": 0.122, "2/0": 0.0967, "3/0": 0.0766, "4/0": 0.0608
        }
        
        if wire_size not in wire_resistance:
            return None
        
        # Calculate voltage drop: VD = 2 × K × I × L / 1000
        # K = resistance per 1000ft, I = current, L = length
        vd = (2 * wire_resistance[wire_size] * current_amps * length_feet) / 1000
        vd_percentage = (vd / voltage) * 100
        
        if vd_percentage > 3:
            return CodeViolation(
                severity="warning",
                code_ref="NEC 210.19(A) FPN No. 4",
                description=f"Voltage drop of {vd_percentage:.2f}% exceeds 3% recommendation. "
                           f"Consider upsizing wire from {wire_size} AWG or reducing circuit length.",
                location=f"{length_feet}ft run"
            )
        return None
    
    def check_wire_ampacity(self, wire_size: str, breaker_amps: int) -> Optional[CodeViolation]:
        """
        Verify wire can handle breaker rating
        NEC 310.16 - Ampacity tables
        """
        if wire_size not in self.wire_ampacity:
            return CodeViolation(
                severity="info",
                code_ref="NEC 310.16",
                description=f"Unable to verify ampacity for {wire_size} AWG wire",
                location=""
            )
        
        wire_rating = self.wire_ampacity[wire_size]
        
        if breaker_amps > wire_rating:
            return CodeViolation(
                severity="critical",
                code_ref="NEC 310.16",
                description=f"⚠️ CRITICAL: {wire_size} AWG wire rated for {wire_rating}A "
                           f"cannot support {breaker_amps}A breaker. Upsize wire immediately.",
                location=""
            )
        
        # Warning if undersized (no safety margin)
        if breaker_amps == wire_rating:
            return CodeViolation(
                severity="warning",
                code_ref="NEC 310.16",
                description=f"Wire at maximum ampacity ({wire_rating}A). Consider upsizing for safety margin.",
                location=""
            )
        
        return None
    
    def check_gfci_required(self, location: str) -> Optional[CodeViolation]:
        """
        Check if GFCI protection required
        NEC 210.8 (A) & (B)
        """
        location_lower = location.lower()
        
        for gfci_loc in self.gfci_locations:
            if gfci_loc in location_lower:
                return CodeViolation(
                    severity="warning",
                    code_ref="NEC 210.8",
                    description=f"GFCI protection required for {location}. Verify GFCI breaker or receptacle.",
                    location=location
                )
        return None
    
    def check_afci_required(self, location: str) -> Optional[CodeViolation]:
        """
        Check if AFCI protection required
        NEC 210.12
        """
        location_lower = location.lower()
        
        for afci_loc in self.afci_locations:
            if afci_loc in location_lower:
                article = "210.12(A)" if self.version == NECVersion.NEC_2023 else "210.12"
                return CodeViolation(
                    severity="warning",
                    code_ref=f"NEC {article}",
                    description=f"AFCI protection required for {location}. Verify AFCI breaker.",
                    location=location
                )
        return None
    
    def check_conduit_fill(self, conduit_size: str, wire_count: int, 
                          wire_sizes: List[str]) -> Optional[CodeViolation]:
        """
        Check conduit fill percentage
        NEC Chapter 9, Table 1
        """
        # Conduit inner diameter (inches) - EMT
        conduit_diameters = {
            "1/2": 0.622, "3/4": 0.824, "1": 1.049, "1-1/4": 1.380,
            "1-1/2": 1.610, "2": 2.067, "2-1/2": 2.469, "3": 3.068, "4": 4.026
        }
        
        # Wire cross-sectional area (sq inches) - THHN
        wire_areas = {
            "14": 0.0097, "12": 0.0133, "10": 0.0211, "8": 0.0366,
            "6": 0.0507, "4": 0.0824, "3": 0.0973, "2": 0.1158,
            "1": 0.1562, "1/0": 0.1855, "2/0": 0.2223, "3/0": 0.2679, "4/0": 0.3237
        }
        
        if conduit_size not in conduit_diameters:
            return None
        
        # Calculate total wire area
        total_wire_area = sum(wire_areas.get(size, 0) for size in wire_sizes)
        
        # Calculate conduit area
        radius = conduit_diameters[conduit_size] / 2
        conduit_area = 3.14159 * (radius ** 2)
        
        # Determine fill limit
        if wire_count == 1:
            max_fill_pct = 53
        elif wire_count == 2:
            max_fill_pct = 31
        else:
            max_fill_pct = 40
        
        # Calculate actual fill
        actual_fill_pct = (total_wire_area / conduit_area) * 100
        
        if actual_fill_pct > max_fill_pct:
            return CodeViolation(
                severity="critical",
                code_ref="NEC Chapter 9, Table 1",
                description=f"⚠️ CRITICAL: {conduit_size}\" conduit at {actual_fill_pct:.1f}% fill "
                           f"(max {max_fill_pct}%). Upsize conduit or reduce wire count.",
                location=""
            )
        
        if actual_fill_pct > (max_fill_pct * 0.8):
            return CodeViolation(
                severity="warning",
                code_ref="NEC Chapter 9, Table 1",
                description=f"{conduit_size}\" conduit at {actual_fill_pct:.1f}% fill. "
                           f"Close to {max_fill_pct}% limit - consider upsizing.",
                location=""
            )
        
        return None
    
    def check_outdoor_requirements(self, text: str) -> List[CodeViolation]:
        """
        Check outdoor installation requirements
        NEC 225, 230, 300.5, 300.6
        """
        violations = []
        
        if any(word in text.lower() for word in ['outdoor', 'exterior', 'outside']):
            violations.append(CodeViolation(
                severity="info",
                code_ref="NEC 300.6(A)",
                description="Outdoor installation: Verify corrosion-resistant materials "
                           "(PVC, rigid galvanized, or stainless steel)",
                location="Outdoor"
            ))
            
            violations.append(CodeViolation(
                severity="info",
                code_ref="NEC 300.5",
                description="Outdoor burial: Minimum 18\" depth for conduit (24\" for direct burial cable)",
                location="Outdoor"
            ))
            
            violations.append(CodeViolation(
                severity="warning",
                code_ref="NEC 110.11",
                description="Weatherproof enclosures required. Verify NEMA 3R or better rating.",
                location="Outdoor"
            ))
        
        return violations
    
    def check_grounding(self, text: str) -> List[CodeViolation]:
        """
        Verify grounding requirements
        NEC Article 250
        """
        violations = []
        
        # Check for service entrance
        if any(word in text.lower() for word in ['service', 'meter', 'main panel']):
            violations.append(CodeViolation(
                severity="info",
                code_ref="NEC 250.24",
                description="Verify grounding electrode system (GES) connection at service equipment",
                location="Service entrance"
            ))
        
        # Check for panels
        if any(word in text.lower() for word in ['panel', 'subpanel', 'distribution']):
            violations.append(CodeViolation(
                severity="info",
                code_ref="NEC 250.32",
                description="Separate building: Verify 4-wire feed or local grounding electrode system",
                location="Subpanel"
            ))
        
        return violations
    
    def generate_code_summary(self) -> Dict[str, any]:
        """Generate summary of code compliance check"""
        critical = [v for v in self.violations if v.severity == "critical"]
        warnings = [v for v in self.violations if v.severity == "warning"]
        info = [v for v in self.violations if v.severity == "info"]
        
        return {
            "nec_version": self.version.value,
            "total_checks": len(self.violations),
            "critical_violations": len(critical),
            "warnings": len(warnings),
            "informational": len(info),
            "violations": [
                {
                    "severity": v.severity,
                    "code_ref": v.code_ref,
                    "description": v.description,
                    "location": v.location
                }
                for v in self.violations
            ]
        }


# Common NEC references for quick lookup
NEC_QUICK_REFERENCE = {
    "210.8": "GFCI Protection - Bathrooms, kitchens, outdoors, basements, garages",
    "210.12": "AFCI Protection - Bedrooms, living areas, hallways",
    "210.19": "Conductor Sizing - Voltage drop recommendations",
    "210.20": "Overcurrent Protection",
    "220": "Branch Circuit, Feeder & Service Load Calculations",
    "225": "Outside Branch Circuits & Feeders",
    "230": "Services - Service entrance requirements",
    "250": "Grounding & Bonding",
    "300.5": "Underground Installations - Burial depths",
    "300.6": "Protection Against Corrosion",
    "310.12": "Conductor Identification - Color coding",
    "310.16": "Ampacity Tables - Conductor current ratings",
    "Chapter 9 Table 1": "Conduit Fill Percentages",
    "Chapter 9 Table 4": "Dimensions of Conduit",
    "Chapter 9 Table 5": "Dimensions of Wire",
    "314": "Outlet, Device, Pull & Junction Boxes",
    "334": "NM Cable (Romex)",
    "358": "EMT - Electrical Metallic Tubing",
    "344": "RMC - Rigid Metal Conduit",
    "352": "PVC - Rigid PVC Conduit",
    "430": "Motors & Motor Controllers",
    "450": "Transformers",
    "517": "Health Care Facilities",
    "680": "Swimming Pools, Fountains & Similar",
    "700": "Emergency Systems",
    "702": "Optional Standby Systems",
    "705": "Interconnected Electric Power Production",
}
