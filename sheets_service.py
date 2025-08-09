import os
import logging
from datetime import datetime, timedelta
import requests
import json
import asyncio
from config import Config
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

class SheetsService:
    def __init__(self):
        self.sheet_url = "https://docs.google.com/spreadsheets/d/1q4g3gQb-8N6MEOi9rxtzf6U-izyQtss9tTn6xBlOCTg/edit?usp=drivesdk"
        self.sheet_id = "1q4g3gQb-8N6MEOi9rxtzf6U-izyQtss9tTn6xBlOCTg"
        self.sheet = None
        self.gc = None
        self._init_sheets()
    
    def _init_sheets(self):
        """Initialize Google Sheets connection using public link with read access"""
        try:
            # Initialize gspread with anonymous access for public sheets
            self.gc = gspread.Client()
            self.sheet = self.gc.open_by_key(self.sheet_id).sheet1
            
            # Create headers if sheet is empty
            self._ensure_headers()
            
            logger.info(f"Google Sheets connected successfully: {self.sheet_id[:10]}...")
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {e}")
            # Fallback to logging mode
            logger.info("Running in logging mode - data will be logged only")
    
    def _ensure_headers(self):
        """Create headers in the sheet if they don't exist"""
        try:
            # Check if headers exist
            headers = ['Tanggal', 'Tipe', 'Jumlah', 'Kategori', 'Keterangan', 'Timestamp']
            
            if self.sheet:
                existing_headers = self.sheet.row_values(1)
                if not existing_headers or existing_headers != headers:
                    # Add headers
                    self.sheet.clear()
                    self.sheet.append_row(headers)
                    logger.info("Headers created in Google Sheets")
                else:
                    logger.info("Headers already exist in Google Sheets")
                    
        except Exception as e:
            logger.error(f"Error ensuring headers: {e}")
    
    async def add_expense(self, date, amount, category, description, type="pengeluaran"):
        """Add expense/income to Google Sheets"""
        try:
            # Format data for the sheet
            row_data = [
                date.strftime('%Y-%m-%d'),  # Tanggal
                type,                       # Tipe
                amount,                     # Jumlah
                category,                   # Kategori
                description,                # Keterangan
                datetime.now().isoformat() # Timestamp
            ]
            
            # Try to add to Google Sheets
            if self.sheet:
                try:
                    self.sheet.append_row(row_data)
                    logger.info(f"Added to Google Sheets - {type}: Rp {amount:,.0f} - {description} [{category}]")
                    return True
                except Exception as sheet_error:
                    logger.error(f"Failed to write to Google Sheets: {sheet_error}")
                    # Fall back to logging
                    logger.info(f"LOGGED {type}: Rp {amount:,.0f} - {description} [{category}]")
                    return True
            else:
                # Log only mode
                logger.info(f"LOGGED {type}: Rp {amount:,.0f} - {description} [{category}]")
                return True
            
        except Exception as e:
            logger.error(f"Error adding expense: {e}")
            return False
    
    async def get_daily_summary(self, date):
        """Get daily summary from Google Sheets"""
        try:
            if not self.sheet:
                return {
                    'expenses': [],
                    'income': [],
                    'message': f'Silakan cek Google Sheets untuk data {date.strftime("%Y-%m-%d")}'
                }
            
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
            return {
                'expenses': [],
                'income': [],
                'message': f'Error mengambil data: {str(e)}'
            }
    
    async def get_custom_summary(self, start_date, end_date):
        """Get custom date range summary from Google Sheets"""
        try:
            if not self.sheet:
                return {
                    'expenses': [],
                    'income': [],
                    'message': f'Silakan cek Google Sheets untuk data {start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")}'
                }
            
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
            return {
                'expenses': [],
                'income': [],
                'message': f'Error mengambil data: {str(e)}'
            }
    
    async def get_monthly_summary(self, date):
        """Get monthly summary from Google Sheets"""
        try:
            if not self.sheet:
                return {
                    'expenses': [],
                    'income': [],
                    'message': f'Silakan cek Google Sheets untuk data bulan {date.strftime("%B %Y")}'
                }
            
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
            return {
                'expenses': [],
                'income': [],
                'message': f'Error mengambil data: {str(e)}'
            }
    
    async def get_yearly_summary(self, year):
        """Get yearly summary from Google Sheets"""
        try:
            if not self.sheet:
                return {
                    'expenses': [],
                    'income': [],
                    'message': f'Silakan cek Google Sheets untuk data tahun {year}'
                }
            
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
            return {
                'expenses': [],
                'income': [],
                'message': f'Error mengambil data: {str(e)}'
            }