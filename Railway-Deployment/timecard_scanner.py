"""
Time Card Scanner - Extract employee hours from time card images
Supports both FTE (Tesla Employee ID) and Contractor (Vendor Employee ID) sheets
"""

import re
from typing import List, Dict, Optional
from datetime import datetime
import io


class TimeCardScanner:
    """Extract employee time data from scanned time cards"""
    
    def __init__(self):
        self.default_scope_id = "64437"
        self.default_po_number = "PO #5100837069"
        self.default_po_line = "110"
        self.default_lunch = "0.50"
        self.default_shift = "Day"
    
    def detect_sheet_type(self, text: str) -> str:
        """
        Determine if this is an FTE or Contractor time sheet
        Returns: 'FTE' or 'Contractor'
        """
        if "Tesla Employee ID" in text or "TESLA EMPLOYEE ID" in text:
            return "FTE"
        elif "Vendor Employee ID" in text or "VENDOR EMPLOYEE ID" in text:
            return "Contractor"
        else:
            # Default to Contractor if unclear
            return "Contractor"
    
    def extract_time_entries(self, text: str) -> List[Dict]:
        """
        Extract time entries from pipe-delimited table format
        Expected: ID | Name | TimeIn | TimeOut | Meal | Shift | Hours
        """
        
        entries = []
        lines = text.split('\n')
        
        print(f"[SCANNER] Processing {len(lines)} lines")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            print(f"[SCANNER] Line {line_num}: {line[:100]}")  # First 100 chars
            
            # Skip header rows
            if any(header in line.upper() for header in ['EMPLOYEE ID', 'FULL NAME', 'TIME IN', 'TIME OUT', 'VENDOR', 'TESLA']):
                print(f"[SCANNER] Line {line_num}: SKIPPED (header)")
                continue
            
            # Check if line has pipe delimiters (table format)
            if '|' in line:
                print(f"[SCANNER] Line {line_num}: Has pipes, splitting...")
                parts = [p.strip() for p in line.split('|')]
                print(f"[SCANNER] Line {line_num}: Split into {len(parts)} parts: {parts}")
                
                # Need at least ID and Name
                if len(parts) < 2:
                    print(f"[SCANNER] Line {line_num}: SKIPPED (not enough parts)")
                    continue
                
                # Column 1: Employee ID (clean to digits only)
                employee_id = ''.join(filter(str.isdigit, parts[0]))
                print(f"[SCANNER] Line {line_num}: Employee ID = '{employee_id}'")
                
                if len(employee_id) < 6:
                    print(f"[SCANNER] Line {line_num}: SKIPPED (ID too short)")
                    continue
                
                # Column 2: Full Name (clean to letters/spaces only)
                full_name = ''.join(c for c in parts[1] if c.isalpha() or c.isspace()).strip()
                print(f"[SCANNER] Line {line_num}: Full Name = '{full_name}'")
                
                if len(full_name) < 3:
                    print(f"[SCANNER] Line {line_num}: SKIPPED (name too short)")
                    continue
                
                # Column 3: Time In (if present)
                time_in = ""
                if len(parts) > 2:
                    time_in = self.extract_time_from_text(parts[2])
                    print(f"[SCANNER] Line {line_num}: Time In = '{time_in}'")
                
                # Column 4: Time Out (if present)
                time_out = ""
                if len(parts) > 3:
                    time_out = self.extract_time_from_text(parts[3])
                    print(f"[SCANNER] Line {line_num}: Time Out = '{time_out}'")
                
                # Column 5: Meal (extract number)
                lunch = self.default_lunch
                if len(parts) > 4:
                    meal_digits = ''.join(filter(str.isdigit, parts[4]))
                    if meal_digits:
                        meal_val = int(meal_digits)
                        if meal_val > 2:  # Minutes
                            lunch = f"{meal_val / 60:.2f}"
                        else:
                            lunch = "0.50"
                    print(f"[SCANNER] Line {line_num}: Lunch = '{lunch}'")
                
                # Column 6: Shift (Day/Night)
                shift = self.default_shift
                if len(parts) > 5:
                    if 'NIGHT' in parts[5].upper() or 'N' in parts[5].upper():
                        shift = "Night"
                    print(f"[SCANNER] Line {line_num}: Shift = '{shift}'")
                
                # Column 7: Total Hours
                hours_worked = ""
                if len(parts) > 6:
                    hours_text = parts[6]
                    hours_match = re.search(r'(\d+\.?\d*)', hours_text)
                    if hours_match:
                        hours_worked = f"{float(hours_match.group(1)):.2f}"
                    print(f"[SCANNER] Line {line_num}: Hours = '{hours_worked}'")
                
                # Calculate if not provided
                if not hours_worked and time_in and time_out:
                    try:
                        hours_worked = self.calculate_hours(time_in, time_out, float(lunch))
                    except:
                        pass
                
                print(f"[SCANNER] Line {line_num}: EXTRACTED ENTRY")
                
            else:
                print(f"[SCANNER] Line {line_num}: No pipes, trying fallback pattern")
                # Fallback: Try original pattern matching for non-table format
                id_match = re.search(r'(\d{6,9})', line)
                if not id_match:
                    print(f"[SCANNER] Line {line_num}: SKIPPED (no ID match)")
                    continue
                
                employee_id = id_match.group(1)
                remaining = line.replace(employee_id, '', 1).strip()
                
                # Extract name
                name_match = re.search(r'^([A-Za-z\s\.\-\']{3,40})', remaining)
                if not name_match:
                    print(f"[SCANNER] Line {line_num}: SKIPPED (no name match)")
                    continue
                
                full_name = name_match.group(1).strip()
                remaining = remaining.replace(full_name, '', 1).strip()
                
                # Extract times
                time_in = self.extract_time_from_text(remaining)
                remaining = remaining.replace(time_in, '', 1) if time_in else remaining
                time_out = self.extract_time_from_text(remaining)
                
                lunch = self.default_lunch
                shift = self.default_shift
                hours_worked = ""
                
                print(f"[SCANNER] Line {line_num}: EXTRACTED ENTRY (fallback)")
            
            # Build entry
            entry = {
                'employee_id': employee_id,
                'full_name': full_name.title(),
                'scope_id': self.default_scope_id,
                'po_number': self.default_po_number,
                'po_line': self.default_po_line,
                'time_in': time_in,
                'time_out': time_out,
                'lunch': lunch,
                'shift': shift,
                'hours_worked': hours_worked,
                'comments': '',
                'has_signature': True
            }
            
            # Flag for review
            flags = []
            if not time_in or not time_out:
                flags.append("REVIEW: Missing times")
            if not hours_worked:
                flags.append("REVIEW: No hours calculated")
            elif float(hours_worked) > 12:
                flags.append("REVIEW: Hours >12")
            elif float(hours_worked) < 1:
                flags.append("REVIEW: Hours <1")
            
            if flags:
                entry['comments'] = "; ".join(flags)
            
            entries.append(entry)
        
        print(f"[SCANNER] Total entries extracted: {len(entries)}")
        return entries
    
    def extract_time_from_text(self, text: str) -> str:
        """
        Extract time from messy OCR text
        Handles: 6:00, 600, 6 00, 17:30, 1730, etc.
        """
        if not text:
            return ""
        
        # Look for time patterns
        # Pattern 1: HH:MM format
        match = re.search(r'(\d{1,2})[:\.](\d{2})', text)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            return self.format_time(hours, minutes)
        
        # Pattern 2: HHMM or HMM (no separator)
        match = re.search(r'(\d{3,4})', text)
        if match:
            time_str = match.group(1)
            if len(time_str) == 4:  # HHMM
                hours = int(time_str[:2])
                minutes = int(time_str[2:])
            else:  # HMM
                hours = int(time_str[0])
                minutes = int(time_str[1:])
            return self.format_time(hours, minutes)
        
        return ""
    
    def format_time(self, hours: int, minutes: int) -> str:
        """Format time with AM/PM"""
        if hours == 0:
            return f"12:{minutes:02d} AM"
        elif hours < 12:
            return f"{hours}:{minutes:02d} AM"
        elif hours == 12:
            return f"12:{minutes:02d} PM"
        else:
            return f"{hours-12}:{minutes:02d} PM"
        """
        Extract individual employee time entries from OCR text
        
        Format expectations:
        - Column 1: ID # (6-9 digits) - TYPED
        - Column 2: Full Name - TYPED  
        - Column 3: Start Time - HANDWRITTEN (may be unclear)
        - Column 4: End Time - HANDWRITTEN (may be unclear)
        - Column 5: Meal Break - HANDWRITTEN (may be unclear)
        - Column 6: Signature - ignore
        - Column 7: Total Hours - HANDWRITTEN (may be unclear)
        
        Strategy: Extract typed names reliably, attempt times, flag unclear entries
        """
        
        entries = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Skip header rows
            if any(header in line.upper() for header in ['EMPLOYEE ID', 'FULL NAME', 'START TIME', 'TIME IN', 'COLUMN']):
                continue
            
            # Extract employee ID (6-9 digit number at start) - TYPED = RELIABLE
            id_match = re.search(r'^(\d{6,9})', line)
            if not id_match:
                continue
            
            employee_id = id_match.group(1)
            remaining_text = line[len(employee_id):].strip()
            
            # Extract full name (typed text before time patterns) - TYPED = RELIABLE
            # Names are words/letters before any time patterns or numbers
            name_match = re.search(r'^([A-Za-z\s\.\-\']+?)(?=\d{1,2}[:\.]?\d{0,2}|\d{1,2}\s*[AP]M|$)', remaining_text)
            full_name = name_match.group(1).strip() if name_match else ""
            
            if not full_name or len(full_name) < 3:
                continue
            
            # Now look for handwritten times - these may be unclear
            # Look for patterns like: 5:00, 530, 5 00, 5:30 AM, 1:30 PM
            time_pattern = r'(\d{1,2}[:\.\s]?\d{0,2}\s*(?:AM|PM|am|pm)?)'
            times = re.findall(time_pattern, remaining_text, re.IGNORECASE)
            
            # Try to extract times, but flag if unclear
            time_in = ""
            time_out = ""
            confidence_low = False
            
            if len(times) >= 2:
                time_in = self.normalize_time(times[0])
                time_out = self.normalize_time(times[1])
            else:
                confidence_low = True
            
            # Extract meal break - look for decimal like 0.5, 0.50, or whole number like 30
            meal_match = re.search(r'(\d+\.?\d*)', remaining_text)
            lunch = self.default_lunch
            if meal_match:
                meal_value = float(meal_match.group(1))
                if meal_value > 2:  # Assume minutes
                    lunch = f"{meal_value / 60:.2f}"
                else:
                    lunch = f"{meal_value:.2f}"
            
            # Try to extract total hours if present
            # Usually at end of line, decimal number
            hours_match = re.search(r'(\d{1,2}\.\d{1,2})$', remaining_text)
            hours_worked = hours_match.group(1) if hours_match else ""
            
            # If we have both times, calculate hours
            if time_in and time_out and not hours_worked:
                try:
                    hours_worked = self.calculate_hours(time_in, time_out, float(lunch))
                except:
                    confidence_low = True
            
            # Build entry
            entry = {
                'employee_id': employee_id,
                'full_name': full_name.title(),
                'scope_id': self.default_scope_id,
                'po_number': self.default_po_number,
                'po_line': self.default_po_line,
                'time_in': time_in,
                'time_out': time_out,
                'lunch': lunch,
                'shift': self.default_shift,
                'hours_worked': hours_worked,
                'comments': '',
                'has_signature': True  # Assume signed
            }
            
            # Flag entries that need review
            flags = []
            
            if not time_in or not time_out:
                flags.append("REVIEW: Missing times")
                confidence_low = True
            
            if confidence_low:
                flags.append("REVIEW: OCR unclear")
            
            if hours_worked:
                hours_float = float(hours_worked) if hours_worked else 0
                if hours_float > 12:
                    flags.append("REVIEW: Hours >12")
                if hours_float < 1:
                    flags.append("REVIEW: Hours <1")
            
            if flags:
                entry['comments'] = "; ".join(flags)
            
            entries.append(entry)
        
        return entries
    
    def normalize_time(self, time_str: str) -> str:
        """
        Normalize various time formats from handwriting OCR
        Input: "530", "5:30", "5 30", "530AM", "5:30 PM"
        Output: "5:30 AM" or "1:30 PM"
        """
        time_str = time_str.strip().upper()
        
        # Remove spaces
        time_str = time_str.replace(' ', '')
        
        # Check for AM/PM
        has_am = 'AM' in time_str
        has_pm = 'PM' in time_str
        time_str = time_str.replace('AM', '').replace('PM', '')
        
        # Handle different separators
        time_str = time_str.replace('.', ':').replace(',', ':')
        
        # If no colon, insert one (e.g., "530" -> "5:30")
        if ':' not in time_str and len(time_str) >= 3:
            time_str = time_str[:-2] + ':' + time_str[-2:]
        
        # Parse hours and minutes
        if ':' in time_str:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
        else:
            hours = int(time_str) if time_str.isdigit() else 0
            minutes = 0
        
        # Determine AM/PM if not specified
        if not has_am and not has_pm:
            # Heuristic: 1-6 likely PM if end time, 7-12 likely AM if start time
            # For now, keep it ambiguous
            if hours >= 7 and hours <= 11:
                suffix = "AM"
            elif hours == 12:
                suffix = "PM"
            elif hours >= 1 and hours <= 6:
                suffix = "PM"
            else:
                suffix = "AM"
        else:
            suffix = "PM" if has_pm else "AM"
        
        return f"{hours}:{minutes:02d} {suffix}"
        
        return entries
    
    def calculate_hours(self, start_time: str, end_time: str, lunch_hours: float = 0.5) -> str:
        """
        Calculate total hours worked between start and end time, minus lunch
        Handles formats like: "5:00 AM", "1:30 PM", "05:00", "13:30"
        """
        try:
            # Parse start time
            start = self.parse_time(start_time)
            # Parse end time
            end = self.parse_time(end_time)
            
            # If end is before start, assume it crosses midnight
            if end <= start:
                end += 24 * 60  # Add 24 hours in minutes
            
            # Calculate difference in hours
            total_minutes = end - start
            total_hours = total_minutes / 60.0
            
            # Subtract lunch
            worked_hours = total_hours - lunch_hours
            
            return f"{worked_hours:.2f}"
        except Exception as e:
            print(f"Error calculating hours: {e}")
            return ""
    
    def parse_time(self, time_str: str) -> int:
        """
        Parse time string to minutes since midnight
        Supports: "5:00 AM", "1:30 PM", "05:00", "13:30"
        Returns: minutes as integer
        """
        time_str = time_str.strip().upper()
        
        # Check for AM/PM
        is_pm = 'PM' in time_str
        is_am = 'AM' in time_str
        
        # Extract HH:MM
        time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
        if not time_match:
            raise ValueError(f"Invalid time format: {time_str}")
        
        hours = int(time_match.group(1))
        minutes = int(time_match.group(2))
        
        # Convert to 24-hour format if AM/PM specified
        if is_pm and hours < 12:
            hours += 12
        elif is_am and hours == 12:
            hours = 0
        
        return hours * 60 + minutes
    
    def validate_entries(self, entries: List[Dict]) -> Dict:
        """
        Validate extracted entries and generate summary
        Returns: validation summary with counts and issues
        """
        total_entries = len(entries)
        missing_times = sum(1 for e in entries if not e['time_in'] or not e['time_out'])
        missing_signatures = sum(1 for e in entries if not e['has_signature'])
        excessive_hours = sum(1 for e in entries if e['hours_worked'] and float(e['hours_worked']) > 12)
        low_hours = sum(1 for e in entries if e['hours_worked'] and float(e['hours_worked']) < 1)
        
        return {
            'total_entries': total_entries,
            'missing_times': missing_times,
            'missing_signatures': missing_signatures,
            'excessive_hours': excessive_hours,
            'low_hours': low_hours,
            'valid_entries': total_entries - missing_times
        }
