import os
import logging
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import json
import asyncio
from config import Config

logger = logging.getLogger(__name__)

class SheetsService:
    def __init__(self):
        self.gc = None
        self.sheet = None
        self._init_sheets()
    
    def _init_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            # Parse service account credentials from environment variable
            if Config.GOOGLE_SHEETS_CREDENTIALS:
                creds_dict = json.loads(Config.GOOGLE_SHEETS_CREDENTIALS)
                scope = ['https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive']
                
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                self.gc = gspread.authorize(creds)
                
                # Open or create spreadsheet
                try:
                    self.sheet = self.gc.open(Config.GOOGLE_SHEETS_NAME).sheet1
                except gspread.SpreadsheetNotFound:
                    # Create new spreadsheet if it doesn't exist
                    spreadsheet = self.gc.create(Config.GOOGLE_SHEETS_NAME)
                    self.sheet = spreadsheet.sheet1
                    # Set up headers
                    self.sheet.append_row(['Tanggal', 'Tipe', 'Jumlah', 'Kategori', 'Keterangan', 'Timestamp'])
                    logger.info(f"Created new spreadsheet: {Config.GOOGLE_SHEETS_NAME}")
                
                logger.info("Google Sheets connection established")
            else:
                logger.warning("Google Sheets credentials not provided")
                
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {e}")
    
    async def add_expense(self, date, amount, category, description, type="pengeluaran"):
        """Add expense/income to Google Sheets"""
        try:
            if not self.sheet:
                logger.error("Google Sheets not initialized")
                return False
            
            # Format data for sheets
            row_data = [
                date.strftime('%Y-%m-%d'),  # Date in ISO format
                type,                       # Type (pengeluaran/pemasukan)
                amount,                     # Amount
                category,                   # Category
                description,                # Description
                datetime.now().isoformat()  # Timestamp
            ]
            
            # Add row to sheet
            self.sheet.append_row(row_data)
            logger.info(f"Added {type}: {amount} - {description}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding expense to sheets: {e}")
            return False
    
    async def get_daily_summary(self, date):
        """Get daily summary from Google Sheets"""
        try:
            if not self.sheet:
                return None
            
            # Get all records
            records = self.sheet.get_all_records()
            
            # Filter by date
            target_date = date.strftime('%Y-%m-%d')
            daily_records = [r for r in records if r.get('Tanggal') == target_date]
            
            # Group by type
            expenses = [r for r in daily_records if r.get('Tipe') == 'pengeluaran']
            income = [r for r in daily_records if r.get('Tipe') == 'pemasukan']
            
            return {
                'expenses': [{'amount': r['Jumlah'], 'category': r['Kategori'], 'description': r['Keterangan']} for r in expenses],
                'income': [{'amount': r['Jumlah'], 'category': r['Kategori'], 'description': r['Keterangan']} for r in income]
            }
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return None
    
    async def get_custom_summary(self, start_date, end_date):
        """Get custom date range summary from Google Sheets"""
        try:
            if not self.sheet:
                return None
            
            # Get all records
            records = self.sheet.get_all_records()
            
            # Filter by date range
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            range_records = []
            for r in records:
                record_date = r.get('Tanggal')
                if record_date and start_str <= record_date <= end_str:
                    range_records.append(r)
            
            # Group by type
            expenses = [r for r in range_records if r.get('Tipe') == 'pengeluaran']
            income = [r for r in range_records if r.get('Tipe') == 'pemasukan']
            
            return {
                'expenses': [{'amount': r['Jumlah'], 'category': r['Kategori'], 'description': r['Keterangan']} for r in expenses],
                'income': [{'amount': r['Jumlah'], 'category': r['Kategori'], 'description': r['Keterangan']} for r in income]
            }
            
        except Exception as e:
            logger.error(f"Error getting custom summary: {e}")
            return None
    
    async def get_monthly_summary(self, date):
        """Get monthly summary from Google Sheets"""
        try:
            if not self.sheet:
                return None
            
            # Get all records
            records = self.sheet.get_all_records()
            
            # Filter by month and year
            target_month = date.strftime('%Y-%m')
            monthly_records = []
            for r in records:
                record_date = r.get('Tanggal')
                if record_date and record_date.startswith(target_month):
                    monthly_records.append(r)
            
            # Group by type
            expenses = [r for r in monthly_records if r.get('Tipe') == 'pengeluaran']
            income = [r for r in monthly_records if r.get('Tipe') == 'pemasukan']
            
            return {
                'expenses': [{'amount': r['Jumlah'], 'category': r['Kategori'], 'description': r['Keterangan']} for r in expenses],
                'income': [{'amount': r['Jumlah'], 'category': r['Kategori'], 'description': r['Keterangan']} for r in income]
            }
            
        except Exception as e:
            logger.error(f"Error getting monthly summary: {e}")
            return None
    
    async def get_yearly_summary(self, year):
        """Get yearly summary from Google Sheets"""
        try:
            if not self.sheet:
                return None
            
            # Get all records
            records = self.sheet.get_all_records()
            
            # Filter by year
            target_year = str(year)
            yearly_records = []
            for r in records:
                record_date = r.get('Tanggal')
                if record_date and record_date.startswith(target_year):
                    yearly_records.append(r)
            
            # Group by type
            expenses = [r for r in yearly_records if r.get('Tipe') == 'pengeluaran']
            income = [r for r in yearly_records if r.get('Tipe') == 'pemasukan']
            
            return {
                'expenses': [{'amount': r['Jumlah'], 'category': r['Kategori'], 'description': r['Keterangan']} for r in expenses],
                'income': [{'amount': r['Jumlah'], 'category': r['Kategori'], 'description': r['Keterangan']} for r in income]
            }
            
        except Exception as e:
            logger.error(f"Error getting yearly summary: {e}")
            return None
