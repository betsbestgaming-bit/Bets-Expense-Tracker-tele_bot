import re
from datetime import datetime, timedelta
from dateutil.parser import parse
import logging

logger = logging.getLogger(__name__)

class DateUtils:
    def __init__(self):
        # Indonesian month names mapping
        self.indonesian_months = {
            'januari': 1, 'jan': 1,
            'februari': 2, 'feb': 2,
            'maret': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'mei': 5,
            'juni': 6, 'jun': 6,
            'juli': 7, 'jul': 7,
            'agustus': 8, 'agu': 8,
            'september': 9, 'sep': 9,
            'oktober': 10, 'okt': 10,
            'november': 11, 'nov': 11,
            'desember': 12, 'des': 12
        }
        
        # Reverse mapping for formatting
        self.month_names = {
            1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
            5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
        }
    
    def parse_indonesian_date(self, date_str):
        """Parse Indonesian date format like '12 Agustus 2025'"""
        try:
            date_str = date_str.strip().lower()
            
            # Pattern: dd month yyyy
            pattern = r'(\d{1,2})\s+(\w+)\s+(\d{4})'
            match = re.match(pattern, date_str)
            
            if match:
                day = int(match.group(1))
                month_name = match.group(2)
                year = int(match.group(3))
                
                month = self.indonesian_months.get(month_name)
                if month:
                    return datetime(year, month, day)
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Indonesian date '{date_str}': {e}")
            return None
    
    def parse_date_range(self, date_str):
        """Parse date range like '12-15 Agustus 2025' or '29 Juli 2025 - 2 Agustus 2025'"""
        try:
            date_str = date_str.strip()
            
            # Pattern 1: dd-dd month yyyy (same month)
            pattern1 = r'(\d{1,2})-(\d{1,2})\s+(\w+)\s+(\d{4})'
            match1 = re.match(pattern1, date_str, re.IGNORECASE)
            
            if match1:
                start_day = int(match1.group(1))
                end_day = int(match1.group(2))
                month_name = match1.group(3).lower()
                year = int(match1.group(4))
                
                month = self.indonesian_months.get(month_name)
                if month:
                    start_date = datetime(year, month, start_day)
                    end_date = datetime(year, month, end_day)
                    return start_date, end_date
            
            # Pattern 2: dd month yyyy - dd month yyyy (different months)
            if ' - ' in date_str:
                parts = date_str.split(' - ')
                if len(parts) == 2:
                    start_date = self.parse_indonesian_date(parts[0])
                    end_date = self.parse_indonesian_date(parts[1])
                    if start_date and end_date:
                        return start_date, end_date
            
            return None, None
            
        except Exception as e:
            logger.error(f"Error parsing date range '{date_str}': {e}")
            return None, None
    
    def parse_month_year(self, date_str):
        """Parse month year format like 'Agustus 2025'"""
        try:
            date_str = date_str.strip().lower()
            
            # Pattern: month yyyy
            pattern = r'(\w+)\s+(\d{4})'
            match = re.match(pattern, date_str)
            
            if match:
                month_name = match.group(1)
                year = int(match.group(2))
                
                month = self.indonesian_months.get(month_name)
                if month:
                    return datetime(year, month, 1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing month year '{date_str}': {e}")
            return None
    
    def format_indonesian_date(self, date):
        """Format datetime to Indonesian date string"""
        try:
            month_name = self.month_names[date.month]
            return f"{date.day} {month_name} {date.year}"
        except Exception as e:
            logger.error(f"Error formatting date: {e}")
            return date.strftime('%d-%m-%Y')
    
    def format_month_year(self, date):
        """Format datetime to Indonesian month year string"""
        try:
            month_name = self.month_names[date.month]
            return f"{month_name} {date.year}"
        except Exception as e:
            logger.error(f"Error formatting month year: {e}")
            return date.strftime('%m-%Y')
