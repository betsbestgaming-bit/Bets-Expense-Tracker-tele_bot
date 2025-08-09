import os
import json
import base64
import logging
from google import genai
from google.genai import types
import asyncio
from config import Config

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
    
    async def extract_expense_from_image(self, image_data):
        """Extract expense information from receipt image using Gemini Vision"""
        try:
            system_prompt = """You are an Indonesian receipt OCR expert. Analyze receipt images and extract expense information.
            
            Extract the following information and respond in JSON format:
            {
                "amount": number (total amount in rupiah, no decimal),
                "category": string (one of: makanan, transportasi, belanja, kesehatan, hiburan, pendidikan, tagihan, lainnya),
                "description": string (brief description in Indonesian),
                "items": array of strings (list of purchased items if visible)
            }
            
            Rules:
            - If no clear amount is found, set amount to 0
            - Choose the most appropriate category based on the items/merchant
            - Description should be concise and in Indonesian
            - Extract text carefully, handle Indonesian currency format
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type="image/jpeg",
                    ),
                    "Analyze this receipt image and extract expense information in JSON format."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                ),
            )
            
            if response.text:
                result = json.loads(response.text)
                
                # Validate result
                if result.get('amount', 0) > 0:
                    return {
                        'amount': float(result['amount']),
                        'category': result.get('category', 'lainnya'),
                        'description': result.get('description', 'Pembelian dari foto struk'),
                        'items': result.get('items', [])
                    }
            
            return None
                
        except Exception as e:
            logger.error(f"Error extracting expense from image: {e}")
            return None
    
    async def transcribe_audio(self, audio_file_path):
        """Transcribe audio file using Gemini (basic text processing for voice notes)"""
        try:
            # For now, we'll return a simple message asking user to type instead
            # Gemini doesn't have direct audio transcription like Whisper
            return "Maaf, fitur voice note belum tersedia. Silakan ketik pesan Anda."
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return None
    
    async def extract_expense_from_text(self, text):
        """Extract expense/income information from text using Gemini"""
        try:
            system_prompt = """You are an Indonesian expense tracking assistant. Analyze text to extract expense or income information.

            Extract information and respond in JSON format:
            {
                "type": string ("pengeluaran" or "pemasukan"),
                "amount": number (amount in rupiah, no decimal),
                "category": string (one of: makanan, transportasi, belanja, kesehatan, hiburan, pendidikan, tagihan, gaji, bonus, investasi, lainnya),
                "description": string (brief description in Indonesian)
            }

            Rules:
            - Detect if it's expense (pengeluaran) or income (pemasukan)
            - Convert text amounts to numbers (e.g., "25 ribu" = 25000, "2 juta" = 2000000)
            - Choose appropriate category based on context
            - If no clear amount is found, set amount to 0
            - Description should be concise and descriptive
            
            Examples of expense indicators: beli, bayar, buat, spend, keluar
            Examples of income indicators: dapat, terima, gaji, bonus, untung, masuk
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Analyze this text for expense/income information: \"{text}\"",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                ),
            )
            
            if response.text:
                result = json.loads(response.text)
                
                # Validate result
                if result.get('amount', 0) > 0:
                    return {
                        'type': result.get('type', 'pengeluaran'),
                        'amount': float(result['amount']),
                        'category': result.get('category', 'lainnya'),
                        'description': result.get('description', 'Transaksi')
                    }
            
            return None
                
        except Exception as e:
            logger.error(f"Error extracting expense from text: {e}")
            return None
