import os
import logging
import io
import tempfile
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from openai_service import OpenAIService
from sheets_service import SheetsService
from date_utils import DateUtils
from config import Config

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.sheets_service = SheetsService()
        self.date_utils = DateUtils()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Selamat datang di Bot Pelacak Pengeluaran!

Saya dapat membantu Anda melacak pengeluaran dan pemasukan dengan berbagai cara:

📸 *Kirim foto struk* - Saya akan membaca dan mencatat pengeluaran
🎤 *Kirim voice note* - Ceritakan pengeluaran Anda
💬 *Gunakan perintah teks*:
   • /pengeluaran [jumlah] [kategori] [keterangan]
   • /pemasukan [jumlah] [kategori] [keterangan]

📊 *Lihat rekap*:
   • /rekapharian [tanggal] - Rekap hari tertentu
   • /rekapcustom [rentang tanggal] - Rekap periode custom
   • /rekapbulanan [bulan tahun] - Rekap bulanan
   • /rekaptahunan [tahun] - Rekap tahunan

Ketik /help untuk panduan lengkap.
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📖 *Panduan Penggunaan Bot Pelacak Pengeluaran*

*🔸 Cara Mencatat Pengeluaran:*

1️⃣ *Foto Struk*
   Kirim foto struk/nota pembelian, bot akan otomatis membaca dan mencatat

2️⃣ *Voice Note*
   Rekam suara: "Beli makan siang 25 ribu di warteg"

3️⃣ *Perintah Teks*
   `/pengeluaran 25000 makanan Makan siang di warteg`
   `/pemasukan 500000 gaji Gaji bulan ini`

*🔸 Cara Melihat Rekap:*

📅 `/rekapharian 12 Agustus 2025` - Rekap tanggal tertentu
📊 `/rekapcustom 12-15 Agustus 2025` - Rekap rentang tanggal
📊 `/rekapcustom 29 Juli 2025 - 2 Agustus 2025` - Rekap lintas bulan
📈 `/rekapbulanan Agustus 2025` - Rekap bulan
📊 `/rekaptahunan 2025` - Rekap tahun

*🔸 Format Tanggal yang Didukung:*
• 12 Agustus 2025
• 12-15 Agustus 2025  
• 29 Juli 2025 - 2 Agustus 2025
• Agustus 2025
• 2025

Semua data akan tersimpan otomatis di Google Sheets Anda! 📊
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def expense_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pengeluaran command"""
        try:
            if len(context.args) < 2:
                await update.message.reply_text(
                    "❌ Format salah!\n\n"
                    "Gunakan: `/pengeluaran [jumlah] [kategori] [keterangan]`\n"
                    "Contoh: `/pengeluaran 25000 makanan Makan siang di warteg`",
                    parse_mode='Markdown'
                )
                return
            
            amount = float(context.args[0])
            category = context.args[1] if len(context.args) > 1 else "lainnya"
            description = " ".join(context.args[2:]) if len(context.args) > 2 else ""
            
            # Save to Google Sheets
            result = await self.sheets_service.add_expense(
                date=datetime.now(),
                amount=amount,
                category=category,
                description=description,
                type="pengeluaran"
            )
            
            if result:
                await update.message.reply_text(
                    f"✅ *Pengeluaran tercatat!*\n\n"
                    f"💰 Jumlah: Rp {amount:,.0f}\n"
                    f"🏷️ Kategori: {category}\n"
                    f"📝 Keterangan: {description}\n"
                    f"📅 Tanggal: {datetime.now().strftime('%d %B %Y')}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Gagal menyimpan pengeluaran. Silakan coba lagi.")
                
        except ValueError:
            await update.message.reply_text("❌ Jumlah harus berupa angka yang valid.")
        except Exception as e:
            logger.error(f"Error in expense_command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
    
    async def income_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pemasukan command"""
        try:
            if len(context.args) < 2:
                await update.message.reply_text(
                    "❌ Format salah!\n\n"
                    "Gunakan: `/pemasukan [jumlah] [kategori] [keterangan]`\n"
                    "Contoh: `/pemasukan 500000 gaji Gaji bulan ini`",
                    parse_mode='Markdown'
                )
                return
            
            amount = float(context.args[0])
            category = context.args[1] if len(context.args) > 1 else "lainnya"
            description = " ".join(context.args[2:]) if len(context.args) > 2 else ""
            
            # Save to Google Sheets
            result = await self.sheets_service.add_expense(
                date=datetime.now(),
                amount=amount,
                category=category,
                description=description,
                type="pemasukan"
            )
            
            if result:
                await update.message.reply_text(
                    f"✅ *Pemasukan tercatat!*\n\n"
                    f"💰 Jumlah: Rp {amount:,.0f}\n"
                    f"🏷️ Kategori: {category}\n"
                    f"📝 Keterangan: {description}\n"
                    f"📅 Tanggal: {datetime.now().strftime('%d %B %Y')}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Gagal menyimpan pemasukan. Silakan coba lagi.")
                
        except ValueError:
            await update.message.reply_text("❌ Jumlah harus berupa angka yang valid.")
        except Exception as e:
            logger.error(f"Error in income_command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
    
    async def daily_summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /rekapharian command"""
        try:
            if not context.args:
                date = datetime.now()
            else:
                date_str = " ".join(context.args)
                date = self.date_utils.parse_indonesian_date(date_str)
                if not date:
                    await update.message.reply_text(
                        "❌ Format tanggal salah!\n\n"
                        "Contoh yang benar: `/rekapharian 12 Agustus 2025`",
                        parse_mode='Markdown'
                    )
                    return
            
            summary = await self.sheets_service.get_daily_summary(date)
            formatted_summary = self._format_summary(summary, f"Rekap Harian - {self.date_utils.format_indonesian_date(date)}")
            await update.message.reply_text(formatted_summary, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in daily_summary_command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat mengambil rekap. Silakan coba lagi.")
    
    async def custom_summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /rekapcustom command"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Format salah!\n\n"
                    "Contoh yang benar:\n"
                    "• `/rekapcustom 12-15 Agustus 2025`\n"
                    "• `/rekapcustom 29 Juli 2025 - 2 Agustus 2025`",
                    parse_mode='Markdown'
                )
                return
            
            date_str = " ".join(context.args)
            start_date, end_date = self.date_utils.parse_date_range(date_str)
            
            if not start_date or not end_date:
                await update.message.reply_text(
                    "❌ Format rentang tanggal salah!\n\n"
                    "Contoh yang benar:\n"
                    "• `/rekapcustom 12-15 Agustus 2025`\n"
                    "• `/rekapcustom 29 Juli 2025 - 2 Agustus 2025`",
                    parse_mode='Markdown'
                )
                return
            
            summary = await self.sheets_service.get_custom_summary(start_date, end_date)
            period_str = f"{self.date_utils.format_indonesian_date(start_date)} - {self.date_utils.format_indonesian_date(end_date)}"
            formatted_summary = self._format_summary(summary, f"Rekap Custom - {period_str}")
            await update.message.reply_text(formatted_summary, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in custom_summary_command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat mengambil rekap. Silakan coba lagi.")
    
    async def monthly_summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /rekapbulanan command"""
        try:
            if not context.args:
                date = datetime.now()
            else:
                date_str = " ".join(context.args)
                date = self.date_utils.parse_month_year(date_str)
                if not date:
                    await update.message.reply_text(
                        "❌ Format bulan salah!\n\n"
                        "Contoh yang benar: `/rekapbulanan Agustus 2025`",
                        parse_mode='Markdown'
                    )
                    return
            
            summary = await self.sheets_service.get_monthly_summary(date)
            formatted_summary = self._format_summary(summary, f"Rekap Bulanan - {self.date_utils.format_month_year(date)}")
            await update.message.reply_text(formatted_summary, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in monthly_summary_command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat mengambil rekap. Silakan coba lagi.")
    
    async def yearly_summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /rekaptahunan command"""
        try:
            if not context.args:
                year = datetime.now().year
            else:
                try:
                    year = int(context.args[0])
                except ValueError:
                    await update.message.reply_text(
                        "❌ Format tahun salah!\n\n"
                        "Contoh yang benar: `/rekaptahunan 2025`",
                        parse_mode='Markdown'
                    )
                    return
            
            summary = await self.sheets_service.get_yearly_summary(year)
            formatted_summary = self._format_summary(summary, f"Rekap Tahunan - {year}")
            await update.message.reply_text(formatted_summary, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in yearly_summary_command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat mengambil rekap. Silakan coba lagi.")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages (receipt OCR)"""
        try:
            await update.message.reply_text("📸 Sedang memproses foto struk...")
            
            # Get the largest photo
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            
            # Download image
            image_data = io.BytesIO()
            await file.download_to_memory(image_data)
            image_data.seek(0)
            
            # Process with OpenAI Vision
            expense_data = await self.openai_service.extract_expense_from_image(image_data.getvalue())
            
            if expense_data:
                # Save to Google Sheets
                result = await self.sheets_service.add_expense(
                    date=datetime.now(),
                    amount=expense_data['amount'],
                    category=expense_data['category'],
                    description=expense_data['description'],
                    type="pengeluaran"
                )
                
                if result:
                    await update.message.reply_text(
                        f"✅ *Pengeluaran dari foto tercatat!*\n\n"
                        f"💰 Jumlah: Rp {expense_data['amount']:,.0f}\n"
                        f"🏷️ Kategori: {expense_data['category']}\n"
                        f"📝 Keterangan: {expense_data['description']}\n"
                        f"📅 Tanggal: {datetime.now().strftime('%d %B %Y')}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ Gagal menyimpan pengeluaran dari foto. Silakan coba lagi.")
            else:
                await update.message.reply_text("❌ Tidak dapat membaca informasi pengeluaran dari foto. Pastikan foto struk jelas dan terbaca.")
                
        except Exception as e:
            logger.error(f"Error in handle_photo: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat memproses foto. Silakan coba lagi.")
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        try:
            await update.message.reply_text("🎤 Sedang memproses voice note...")
            
            # Get voice file
            voice = update.message.voice
            file = await context.bot.get_file(voice.file_id)
            
            # Download voice file to temporary location
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                await file.download_to_path(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Transcribe audio
                transcription = await self.openai_service.transcribe_audio(temp_path)
                
                if transcription:
                    # Process transcription to extract expense data
                    expense_data = await self.openai_service.extract_expense_from_text(transcription)
                    
                    if expense_data:
                        # Save to Google Sheets
                        result = await self.sheets_service.add_expense(
                            date=datetime.now(),
                            amount=expense_data['amount'],
                            category=expense_data['category'],
                            description=expense_data['description'],
                            type=expense_data['type']
                        )
                        
                        if result:
                            type_text = "Pengeluaran" if expense_data['type'] == "pengeluaran" else "Pemasukan"
                            await update.message.reply_text(
                                f"✅ *{type_text} dari voice note tercatat!*\n\n"
                                f"🎤 Yang Anda katakan: \"{transcription}\"\n\n"
                                f"💰 Jumlah: Rp {expense_data['amount']:,.0f}\n"
                                f"🏷️ Kategori: {expense_data['category']}\n"
                                f"📝 Keterangan: {expense_data['description']}\n"
                                f"📅 Tanggal: {datetime.now().strftime('%d %B %Y')}",
                                parse_mode='Markdown'
                            )
                        else:
                            await update.message.reply_text("❌ Gagal menyimpan data dari voice note. Silakan coba lagi.")
                    else:
                        await update.message.reply_text(
                            f"❌ Tidak dapat memahami informasi pengeluaran/pemasukan dari: \"{transcription}\"\n\n"
                            "Coba ucapkan dengan format: \"Beli makan siang 25 ribu\" atau \"Dapat gaji 5 juta\""
                        )
                else:
                    await update.message.reply_text("❌ Tidak dapat memproses voice note. Silakan coba lagi.")
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Error in handle_voice: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat memproses voice note. Silakan coba lagi.")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        try:
            text = update.message.text
            
            # Try to extract expense data from text
            expense_data = await self.openai_service.extract_expense_from_text(text)
            
            if expense_data:
                # Save to Google Sheets
                result = await self.sheets_service.add_expense(
                    date=datetime.now(),
                    amount=expense_data['amount'],
                    category=expense_data['category'],
                    description=expense_data['description'],
                    type=expense_data['type']
                )
                
                if result:
                    type_text = "Pengeluaran" if expense_data['type'] == "pengeluaran" else "Pemasukan"
                    await update.message.reply_text(
                        f"✅ *{type_text} tercatat!*\n\n"
                        f"💰 Jumlah: Rp {expense_data['amount']:,.0f}\n"
                        f"🏷️ Kategori: {expense_data['category']}\n"
                        f"📝 Keterangan: {expense_data['description']}\n"
                        f"📅 Tanggal: {datetime.now().strftime('%d %B %Y')}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ Gagal menyimpan data. Silakan coba lagi.")
            else:
                await update.message.reply_text(
                    "❓ Saya tidak mengerti pesan Anda. Gunakan /help untuk melihat panduan penggunaan."
                )
                
        except Exception as e:
            logger.error(f"Error in handle_text: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
    
    def _format_summary(self, summary, title):
        """Format summary data for display"""
        if not summary or (not summary.get('expenses') and not summary.get('income')):
            return f"📊 *{title}*\n\n❌ Tidak ada data untuk periode ini."
        
        message = f"📊 *{title}*\n\n"
        
        # Income summary
        if summary.get('income'):
            total_income = sum(item['amount'] for item in summary['income'])
            message += f"💰 *Total Pemasukan: Rp {total_income:,.0f}*\n"
            
            # Group by category
            income_by_category = {}
            for item in summary['income']:
                category = item['category']
                if category not in income_by_category:
                    income_by_category[category] = 0
                income_by_category[category] += item['amount']
            
            for category, amount in income_by_category.items():
                message += f"  • {category}: Rp {amount:,.0f}\n"
            message += "\n"
        
        # Expense summary
        if summary.get('expenses'):
            total_expenses = sum(item['amount'] for item in summary['expenses'])
            message += f"💸 *Total Pengeluaran: Rp {total_expenses:,.0f}*\n"
            
            # Group by category
            expenses_by_category = {}
            for item in summary['expenses']:
                category = item['category']
                if category not in expenses_by_category:
                    expenses_by_category[category] = 0
                expenses_by_category[category] += item['amount']
            
            for category, amount in expenses_by_category.items():
                message += f"  • {category}: Rp {amount:,.0f}\n"
            message += "\n"
        
        # Net summary
        total_income = sum(item['amount'] for item in summary.get('income', []))
        total_expenses = sum(item['amount'] for item in summary.get('expenses', []))
        net = total_income - total_expenses
        
        if net > 0:
            message += f"📈 *Saldo Bersih: +Rp {net:,.0f}*"
        elif net < 0:
            message += f"📉 *Saldo Bersih: -Rp {abs(net):,.0f}*"
        else:
            message += f"⚖️ *Saldo Bersih: Rp 0*"
        
        return message
