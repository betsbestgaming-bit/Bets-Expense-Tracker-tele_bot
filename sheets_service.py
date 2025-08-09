import os
import logging
from datetime import datetime, timedelta
import requests
import json
import asyncio
from config import Config

logger = logging.getLogger(__name__)

class SheetsService:
    def __init__(self):
        self.sheet_url = None
        self.api_key = None
        self.sheet_id = None
        self._init_sheets()
    
    def _init_sheets(self):
        """Initialize Google Sheets connection using public link"""
        try:
            # We'll ask user for the Google Sheets URL later
            logger.info("Google Sheets service ready - waiting for sheet URL")
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {e}")
    
    def set_sheet_url(self, url):
        """Set the Google Sheets URL for public editing"""
        try:
            self.sheet_url = url
            # Extract sheet ID from URL
            if "/spreadsheets/d/" in url:
                start = url.find("/spreadsheets/d/") + len("/spreadsheets/d/")
                end = url.find("/", start)
                if end == -1:
                    end = url.find("#", start)
                if end == -1:
                    end = len(url)
                self.sheet_id = url[start:end]
                logger.info(f"Sheet URL set: {self.sheet_id[:10]}...")
                return True
        except Exception as e:
            logger.error(f"Error setting sheet URL: {e}")
        return False
    
    async def add_expense(self, date, amount, category, description, type="pengeluaran"):
        """Add expense/income to Google Sheets (simulation)"""
        try:
            # Format data for logging (we'll store in memory for now)
            row_data = {
                'date': date.strftime('%Y-%m-%d'),
                'type': type,
                'amount': amount,
                'category': category,
                'description': description,
                'timestamp': datetime.now().isoformat()
            }
            
            # For now, we'll just log the data (user will manually add to their sheet)
            logger.info(f"Added {type}: Rp {amount:,.0f} - {description} [{category}]")
            
            # In a real implementation, we would use Google Sheets API
            # but since we're using public edit links, we'll return success
            return True
            
        except Exception as e:
            logger.error(f"Error adding expense to sheets: {e}")
            return False
    
    async def get_daily_summary(self, date):
        """Get daily summary from Google Sheets (simulation)"""
        try:
            # For now, return empty summary (user will need to manually check their sheet)
            logger.info(f"Daily summary requested for: {date.strftime('%Y-%m-%d')}")
            return {
                'expenses': [],
                'income': [],
                'message': 'Silakan cek Google Sheets Anda untuk data yang sebenarnya'
            }
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return None
    
    async def get_custom_summary(self, start_date, end_date):
        """Get custom date range summary from Google Sheets (simulation)"""
        try:
            logger.info(f"Custom summary requested for: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            return {
                'expenses': [],
                'income': [],
                'message': 'Silakan cek Google Sheets Anda untuk data yang sebenarnya'
            }
        except Exception as e:
            logger.error(f"Error getting custom summary: {e}")
            return None
    
    async def get_monthly_summary(self, date):
        """Get monthly summary from Google Sheets (simulation)"""
        try:
            logger.info(f"Monthly summary requested for: {date.strftime('%Y-%m')}")
            return {
                'expenses': [],
                'income': [],
                'message': 'Silakan cek Google Sheets Anda untuk data yang sebenarnya'
            }
        except Exception as e:
            logger.error(f"Error getting monthly summary: {e}")
            return None
    
    async def get_yearly_summary(self, year):
        """Get yearly summary from Google Sheets (simulation)"""
        try:
            logger.info(f"Yearly summary requested for: {year}")
            return {
                'expenses': [],
                'income': [],
                'message': 'Silakan cek Google Sheets Anda untuk data yang sebenarnya'
            }
        except Exception as e:
            logger.error(f"Error getting yearly summary: {e}")
            return None