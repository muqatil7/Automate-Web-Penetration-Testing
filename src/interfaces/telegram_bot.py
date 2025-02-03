# src/interfaces/telegram_bot.py

import asyncio
import logging
import sys
import re
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional, List, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from src.app import CyberToolkit
from src.interfaces.ui_manager import UIManager
from src.core.execution_status import ExecutionStatusManager


# =============================================================================
# UI Manager خاص بتنسيق الردود لتيليجرام
# =============================================================================
class TelegramUIManager(UIManager):
    """Custom UI Manager for Telegram that formats output for Telegram messages."""

    def __init__(self, bot: Optional[Any] = None, chat_id: Optional[int] = None):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id
        self.output_buffer = StringIO()
        self.console.file = self.output_buffer

    async def send_progress(self, message: str) -> None:
        """Send progress update to Telegram."""
        if self.bot and self.chat_id:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=f"🔄 {message}",
                parse_mode="Markdown"
            )

    def list_tools(self, tools: Dict[str, Dict[str, Any]]) -> str:
        """Format and return a list of available tools for Telegram."""
        message = "*Available Security Tools:*\n\n"
        for name, tool in tools.items():
            message += f"🔹 *{name}*\n"
            message += f"  └ {tool['description']}\n\n"
        return message

    def display_results(self, results: List[Dict[str, Any]]) -> str:
        """Format and return scan results for Telegram."""
        message = "*🎯 Scan Results:*\n\n"
        for result in results:
            status_icon = "✅" if result.get("exit_code") == 0 else "❌"
            tool_name = result.get("tool", "unknown")
            error = result.get("error", "")
            message += f"{status_icon} *{tool_name}*\n"
            message += f"  └ Status: {status_icon} {'Success' if status_icon == '✅' else 'Failed'}\n"
            if error:
                message += f"  └ Error: `{error}`\n"
            message += f"  └ Log: `{result.get('log_path', 'N/A')}`\n\n"
        return message

    def show_scan_start(self, target: str, num_tools: int, workers: int) -> str:
        """Return a formatted message indicating the start of a scan."""
        return (
            f"🎯 *New Scan Started*\n\n"
            f"Target: `{target}`\n"
            f"Tools: {num_tools}\n"
            f"Workers: {workers}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )


# =============================================================================
# Telegram Bot Class
# =============================================================================
class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.cyber_toolkit = CyberToolkit()
        self.active_scans: Dict[int, Dict[str, Any]] = {}
        self.start_time = datetime.now()

    # -------------------------------------------------------------------------
    # Handler للأوامر
    # -------------------------------------------------------------------------
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command by sending a welcome message with bot info."""
        tool_count = len(self.cyber_toolkit.tm.tools)
        welcome_message = (
            "🛡️ *Cyber Security Tool Bot*\n\n"
            "Welcome to your security assessment assistant!\n\n"
            "*Status Information:*\n"
            "🔹 Bot Version: 1.0.0\n"
            f"🔹 Available Tools: {tool_count}\n"
            "🔹 Status: Active\n"
            f"🔹 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "*Quick Start:*\n"
            "1️⃣ Use /list to see available tools\n"
            "2️⃣ Use /scan to start assessment\n"
            "3️⃣ Use /help for detailed usage\n\n"
            "⚠️ *Security Notice:*\n"
            "Please ensure you have authorization before scanning any target."
        )

        await update.message.reply_text(welcome_message, parse_mode="Markdown")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command by displaying available commands and usage examples."""
        help_text = (
            "*Available Commands:*\n\n"
            "/start - Show welcome message and status\n"
            "/scan - Start a new security assessment\n"
            "/list - Show available security tools\n"
            "/status - View current bot and scan status\n"
            "/help - Show this help message\n\n"
            "*Scan Usage:*\n"
            "`/scan <target> [workers] [mode]`\n\n"
            "*Examples:*\n"
            "• `/scan example.com` - Default scan\n"
            "• `/scan example.com 4 all` - All tools\n"
            "• `/scan example.com 2 tool1,tool2` - Specific tools\n\n"
            "*Parameters:*\n"
            "• target: URL or IP to scan\n"
            "• workers: Number of parallel tasks (default: 4)\n"
            "• mode: 'all' or specific tool names"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def list_tools(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /list command by listing available tools."""
        ui_manager = TelegramUIManager()
        message = ui_manager.list_tools(self.cyber_toolkit.tm.tools)
        await update.message.reply_text(message, parse_mode="Markdown")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /status command by showing detailed bot and scan status with an interactive keyboard."""
        status_manager = ExecutionStatusManager()
        status_manager.load_status()
        summary = status_manager.get_summary()

        keyboard = [
            [
                InlineKeyboardButton("🔍 Tool Details", callback_data="tool_details"),
                InlineKeyboardButton("📊 Scan Summary", callback_data="scan_summary"),
            ],
            [InlineKeyboardButton("🛠️ System Info", callback_data="system_info")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        status_message = (
            "🤖 *Bot Status Overview*\n\n"
            "*Scan Execution:*\n"
            f"• Total Operations: {summary['total']}\n"
            f"• Completed: {summary['completed']}\n"
            f"• Failed: {summary['failed']}\n"
            f"• In Progress: {summary['in_progress']}\n\n"
            "*Bot Information:*\n"
            "• Version: 1.0.0\n"
            f"• Active Since: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            "• Running Mode: Security Assessment\n\n"
            "*Quick Actions:*\n"
            "Select an option below for more details."
        )

        await update.message.reply_text(
            status_message, reply_markup=reply_markup, parse_mode="Markdown"
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all callback queries from inline keyboards."""
        query = update.callback_query
        await query.answer()

        status_manager = ExecutionStatusManager()
        status_manager.load_status()

        if query.data == "tool_details":
            operations = status_manager.get_all_operations()
            details_message = "*🔍 Tool Execution Details:*\n\n"
            for op in operations:
                details_message += f"*{op.tool_name}*\n"
                details_message += f"• Status: {op.status}\n"
                details_message += f"• Start Time: {op.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                details_message += f"• End Time: {op.end_time.strftime('%Y-%m-%d %H:%M:%S') if op.end_time else 'N/A'}\n\n"
            await query.edit_message_text(details_message, parse_mode="Markdown")

        elif query.data == "scan_summary":
            summary = status_manager.get_summary()
            summary_message = (
                "📊 *Detailed Scan Summary*\n\n"
                f"• Total Scan Operations: {summary['total']}\n"
                f"• Successfully Completed: {summary['completed']}\n"
                f"• Failed Operations: {summary['failed']}\n"
                f"• Operations In Progress: {summary['in_progress']}\n\n"
                "*Performance Metrics:*\n"
                f"• Success Rate: {(summary['completed'] / summary['total'] * 100) if summary['total'] > 0 else 0:.2f}%\n"
                f"• Failure Rate: {(summary['failed'] / summary['total'] * 100) if summary['total'] > 0 else 0:.2f}%"
            )
            await query.edit_message_text(summary_message, parse_mode="Markdown")

        elif query.data == "system_info":
            system_message = (
                "🖥️ *System Information*\n\n"
                f"• Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"• Python Version: {sys.version.split()[0]}\n"
                f"• Active Tools: {len(self.cyber_toolkit.tm.tools)}\n"
                "• Current Mode: Security Assessment\n"
                f"• Bot Uptime: {datetime.now() - self.start_time}"
            )
            await query.edit_message_text(system_message, parse_mode="Markdown")

        # التعامل مع أزرار إدارة عمليات الفحص
        elif query.data == "scan_cancel":
            self.active_scans.pop(query.message.chat_id, None)
            await query.edit_message_text("🚫 Scan cancelled!")

        elif query.data == "scan_confirm":
            scan_info = self.active_scans.get(query.message.chat_id)
            if not scan_info:
                await query.edit_message_text("❌ Scan configuration not found!")
                return

            await query.edit_message_text("Scan started! You'll receive progress updates...")
            asyncio.create_task(self.execute_scan(query.message.chat_id, scan_info, context))

    async def execute_scan(self, chat_id: int, scan_info: Dict[str, Any], context: ContextTypes.DEFAULT_TYPE) -> None:
        """Execute the scan with real-time updates to the user."""
        ui_manager = TelegramUIManager(context.bot, chat_id)
        self.cyber_toolkit.ui = ui_manager

        # إرسال رسالة أولية للمستخدم قبل بدء الفحص
        await context.bot.send_message(
            chat_id=chat_id,
            text="🚀 *Initializing Scan*\n\nPreparing tools...",
            parse_mode="Markdown"
        )

        try:
            # تحضير البيئة والتنفيذ
            await ui_manager.send_progress("Setting up environment...")
            self.cyber_toolkit.prepare_environment(scan_info["tools"])

            await ui_manager.send_progress(
                f"Starting scan on `{scan_info['target']}`\n"
                f"Running {len(scan_info['tools'])} tools with {scan_info['workers']} workers"
            )

            # تنفيذ الأدوات المحددة
            results = self.cyber_toolkit.execute_tools(
                scan_info["tools"],
                scan_info["target"],
                scan_info["workers"]
            )

            # عرض ملخص الفحص
            status_manager = ExecutionStatusManager()
            status_manager.load_status()
            summary = status_manager.get_summary()
            summary_message = (
                "📊 *Scan Summary*:\n\n"
                f"- Total Operations: {summary['total']}\n"
                f"- Completed: {summary['completed']}\n"
                f"- Failed: {summary['failed']}\n"
                f"- In Progress: {summary['in_progress']}\n\n"
                "👆 For more details, use /status command."
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=summary_message,
                parse_mode="Markdown"
            )

            # رسالة انتهاء الفحص
            await context.bot.send_message(
                chat_id=chat_id,
                text="✅ *Scan Completed*\nAll tools have finished execution.",
                parse_mode="Markdown"
            )

        except Exception as e:
            # التقاط الأخطاء وإعلام المستخدم بها
            exc_type, exc_obj, exc_tb = sys.exc_info()
            line_number = exc_tb.tb_lineno if exc_tb else "N/A"
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ *Error During Scan*\n`{str(e)}`\nOccurred at line: {line_number}",
                parse_mode="Markdown"
            )
        finally:
            self.active_scans.pop(chat_id, None)

    async def scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /scan command, validate input, and prompt the user for confirmation."""
        if not context.args:
            usage_message = (
                "⚠️ *Scan Usage:*\n\n"
                "`/scan <target> [workers] [mode]`\n\n"
                "*Examples:*\n"
                "• `/scan example.com` - Scan with defaults\n"
                "• `/scan example.com 4 all` - All tools\n"
                "• `/scan example.com 2 tool1,tool2` - Specific tools\n\n"
                "*Defaults:*\n"
                "• Workers: 4\n"
                "• Mode: all"
            )
            await update.message.reply_text(usage_message, parse_mode="Markdown")
            return

        target = context.args[0]
        workers = int(context.args[1]) if len(context.args) > 1 and context.args[1].isdigit() else 4
        mode = context.args[2] if len(context.args) > 2 else "all"

        # التحقق من صيغة الهدف
        if not target or " " in target:
            await update.message.reply_text("❌ *Error:* Invalid target format", parse_mode="Markdown")
            return

        # تحديد الأدوات التي ستستخدم في الفحص
        tools_input = [] if mode.lower() == "all" else mode.split(",")
        tools_to_run = self.cyber_toolkit.validate_and_prepare_tools(tools_input)

        if not tools_to_run:
            await update.message.reply_text("❌ *Error:* No valid tools selected", parse_mode="Markdown")
            return

        chat_id = update.effective_chat.id
        self.active_scans[chat_id] = {
            "target": target,
            "tools": tools_to_run,
            "workers": workers,
        }

        # إعداد لوحة التأكيد باستخدام أزرار Inline Keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ Start Scan", callback_data="scan_confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data="scan_cancel"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        confirm_message = (
            "🎯 *Scan Configuration*\n\n"
            f"• Target: `{target}`\n"
            f"• Workers: {workers}\n"
            f"• Tools: {len(tools_to_run)}\n"
            f"• Mode: {mode}\n\n"
            "*Selected Tools:*\n"
            f"{', '.join(t['name'] for t in tools_to_run)}\n\n"
            "Please confirm to start the scan:"
        )

        await update.message.reply_text(
            confirm_message, reply_markup=reply_markup, parse_mode="Markdown"
        )

    # -------------------------------------------------------------------------
    # إعداد وتشغيل التطبيق
    # -------------------------------------------------------------------------
    def run(self) -> None:
        """Initialize the Telegram bot, register command handlers, set default commands, and start polling."""
        app = Application.builder().token(self.token).build()

        # تسجيل الأوامر
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(CommandHandler("list", self.list_tools))
        app.add_handler(CommandHandler("scan", self.scan))
        app.add_handler(CommandHandler("status", self.status))
        app.add_handler(CallbackQueryHandler(self.button_callback))

        # إعداد أوامر البوت الافتراضية (تظهر للمستخدم في واجهة تيليجرام)
        commands = [
            BotCommand("start", "Show welcome message and status"),
            BotCommand("help", "Show help information"),
            BotCommand("list", "List available security tools"),
            BotCommand("scan", "Start a new security assessment"),
            BotCommand("status", "View bot and scan status"),
        ]
        # يتم تعيينها عند بدء التطبيق
        async def set_commands(app: Application) -> None:
            await app.bot.set_my_commands(commands)

        app.post_init = set_commands  # post_init callback ليتم استدعاؤه بعد تهيئة التطبيق

        # بدء polling
        app.run_polling()

# =============================================================================