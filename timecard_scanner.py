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
        Extract individual employee time entries from OCR text
        
        Expected format per row:
        - Column 1: ID # (6-9 digits)
        - Column 2: Full Name
        - Column 3: Start Time (e.g., "5:00 AM", "05:00", blank)
        - Column 4: End Time (e.g., "1:30 PM", "13:30", blank)
        - Column 5: Meal Break (e.g., "0.50", "0.5", "30 min")
        - Column 6: Signature (check if present)
        - Column 7: Total Hours (e.g., "8.00", "8")
        """
        
        entries = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Skip header rows
            if any(header in line.upper() for header in ['EMPLOYEE ID', 'FULL NAME', 'START TIME', 'COLUMN']):
                continue
            
            # Try to extract employee ID (6-9 digit number at start)
            id_match = re.search(r'^(\d{6,9})', line)
            if not id_match:
                continue
            
            employee_id = id_match.group(1)
            remaining_text = line[len(employee_id):].strip()
            
            # Extract full name (next word(s) before time patterns)
            name_match = re.search(r'^([A-Za-z\s\.]+?)(?=\d{1,2}:\d{2}|AM|PM|$)', remaining_text)
            full_name = name_match.group(1).strip() if name_match else ""
            
            if not full_name:
                continue
            
            # Extract times (look for HH:MM patterns with optional AM/PM)
            time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM)?)'
            times = re.findall(time_pattern, remaining_text, re.IGNORECASE)
            
            time_in = times[0] if len(times) > 0 else ""
            time_out = times[1] if len(times) > 1 else ""
            
            # Extract meal break (look for 0.5, 0.50, 30, etc.)
            meal_match = re.search(r'(\d+\.?\d*)\s*(?:min|minutes|hr)?', remaining_text)
            lunch = self.default_lunch  # Default to 0.50
            if meal_match:
                meal_value = float(meal_match.group(1))
                # Convert minutes to decimal hours if needed
                if meal_value > 2:  # Assume it's in minutes
                    lunch = f"{meal_value / 60:.2f}"
                else:
                    lunch = f"{meal_value:.2f}"
            
            # Calculate hours worked if both times present
            hours_worked = ""
            if time_in and time_out:
                try:
                    hours_worked = self.calculate_hours(time_in, time_out, float(lunch))
                except:
                    hours_worked = ""
            
            # Check for signature indicators
            has_signature = bool(re.search(r'sign|signature|✓|x', remaining_text, re.IGNORECASE))
            
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
                'has_signature': has_signature
            }
            
            # Add validation flags to comments
            flags = []
            if not time_in or not time_out:
                flags.append("Missing time")
            if not has_signature:
                flags.append("No signature")
            if hours_worked and float(hours_worked) > 12:
                flags.append("Hours >12")
            if hours_worked and float(hours_worked) < 1:
                flags.append("Hours <1")
            
            if flags:
                entry['comments'] = "; ".join(flags)
            
            entries.append(entry)
        
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
