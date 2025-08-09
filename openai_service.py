import os
import json
import base64
import logging
from openai import OpenAI
import asyncio
from config import Config

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def extract_expense_from_image(self, image_data):
        """Extract expense information from receipt image using OpenAI Vision"""
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an Indonesian receipt OCR expert. Analyze receipt images and extract expense information.
                        
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
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this receipt image and extract expense information in JSON format."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate result
            if result.get('amount', 0) > 0:
                return {
                    'amount': float(result['amount']),
                    'category': result.get('category', 'lainnya'),
                    'description': result.get('description', 'Pembelian dari foto struk'),
                    'items': result.get('items', [])
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extracting expense from image: {e}")
            return None
    
    async def transcribe_audio(self, audio_file_path):
        """Transcribe audio file using OpenAI Whisper"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="id"  # Indonesian
                )
            return response.text
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def extract_expense_from_text(self, text):
        """Extract expense/income information from text using OpenAI GPT"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an Indonesian expense tracking assistant. Analyze text to extract expense or income information.

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
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this text for expense/income information: \"{text}\""
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate result
            if result.get('amount', 0) > 0:
                return {
                    'type': result.get('type', 'pengeluaran'),
                    'amount': float(result['amount']),
                    'category': result.get('category', 'lainnya'),
                    'description': result.get('description', 'Transaksi')
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extracting expense from text: {e}")
            return None
