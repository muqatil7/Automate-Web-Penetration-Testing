# src/interfaces/telegram_bot.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from src.app import CyberToolkit
from src.interfaces.ui_manager import UIManager
from src.core.execution_status import ExecutionStatusManager

import logging
import asyncio
import sys
import re
from datetime import datetime
from io import StringIO
from typing import Optional, List, Dict, Any
from pathlib import Path

class TelegramUIManager(UIManager):
    """Custom UI Manager for Telegram that formats output for Telegram"""
    def __init__(self, bot: Optional[Any] = None, chat_id: Optional[int] = None):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id
        self.output_buffer = StringIO()
        self.console.file = self.output_buffer

    async def send_progress(self, message: str) -> None:
        """Send progress update to Telegram"""
        if self.bot and self.chat_id:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=f"🔄 {message}",
                parse_mode='Markdown'
            )

    def list_tools(self, tools: Dict[str, Dict[str, Any]]) -> str:
        """Override list_tools to format for Telegram"""
        message = "*Available Security Tools:*\n\n"
        for name, tool in tools.items():
            message += f"🔹 *{name}*\n"
            message += f"  └ {tool['description']}\n\n"
        return message

    def display_results(self, results: List[Dict[str, Any]]) -> str:
        """Override display_results to format for Telegram"""
        message = "*🎯 Scan Results:*\n\n"
        for result in results:
            status = "✅" if result.get('exit_code') == 0 else "❌"
            tool_name = result.get('tool', 'unknown')
            error = result.get('error', '')
            message += f"{status} *{tool_name}*\n"
            message += f"└ Status: {status} {'Success' if status == '✅' else 'Failed'}\n"
            if error:
                message += f"└ Error: `{error}`\n"
            message += f"└ Log: `{result.get('log_path', 'N/A')}`\n\n"
        return message

    def show_scan_start(self, target: str, num_tools: int, workers: int) -> str:
        """Override scan_start to format for Telegram"""
        return (
            f"🎯 *New Scan Started*\n\n"
            f"Target: `{target}`\n"
            f"Tools: {num_tools}\n"
            f"Workers: {workers}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.cyber_toolkit = CyberToolkit()
        self.active_scans: Dict[int, Dict[str, Any]] = {}
        self.start_time = datetime.now()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        welcome_message = """🛡️ *Cyber Security Tool Bot*

Welcome to your security assessment assistant!

*Status Information:*
🔹 Bot Version: 1.0.0
🔹 Available Tools: {tool_count}
🔹 Status: Active
🔹 Last Update: {date}

*Quick Start:*
1️⃣ Use /list to see available tools
2️⃣ Use /scan to start assessment
3️⃣ Use /help for detailed usage

⚠️ *Security Notice:*
Please ensure you have authorization
before scanning any target."""

        tool_count = len(self.cyber_toolkit.tm.tools)
        await update.message.reply_text(
            welcome_message.format(
                tool_count=tool_count,
                date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ),
            parse_mode='Markdown'
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_text = """*Available Commands:*

/start - Show welcome message and status
/scan - Start a new security assessment
/list - Show available security tools
/status - View current bot and scan status
/help - Show this help message

*Scan Usage:*
`/scan <target> [workers] [mode]`

*Examples:*
• `/scan example.com` - Default scan
• `/scan example.com 4 all` - All tools
• `/scan example.com 2 tool1,tool2` - Specific tools

*Parameters:*
• target: URL or IP to scan
• workers: Number of parallel tasks (default: 4)
• mode: 'all' or specific tool names"""

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def list_tools(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /list command"""
        ui_manager = TelegramUIManager()
        message = ui_manager.list_tools(self.cyber_toolkit.tm.tools)
        await update.message.reply_text(message, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command to show detailed bot and scan status"""
        status_manager = ExecutionStatusManager()
        status_manager.load_status()
        summary = status_manager.get_summary()

        # Prepare keyboard for interactive status view
        keyboard = [
            [
                InlineKeyboardButton("🔍 Tool Details", callback_data='tool_details'),
                InlineKeyboardButton("📊 Scan Summary", callback_data='scan_summary')
            ],
            [
                InlineKeyboardButton("🛠️ System Info", callback_data='system_info')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        status_message = f"""🤖 *Bot Status Overview*

*Scan Execution:*
• Total Operations: {summary['total']}
• Completed: {summary['completed']}
• Failed: {summary['failed']}
• In Progress: {summary['in_progress']}

*Bot Information:*
• Version: 1.0.0
• Active Since: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
• Running Mode: Security Assessment

*Quick Actions:*
Select an option below for more details."""

        await update.message.reply_text(
            status_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Enhanced button callback to handle status-related interactions"""
        query = update.callback_query
        await query.answer()

        status_manager = ExecutionStatusManager()
        status_manager.load_status()

        if query.data == 'tool_details':
            operations = status_manager.get_all_operations()
            details_message = "*🔍 Tool Execution Details:*\n\n"
            for op in operations:
                details_message += f"*{op.tool_name}*\n"
                details_message += f"• Status: {op.status}\n"
                details_message += f"• Start Time: {op.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                details_message += f"• End Time: {op.end_time.strftime('%Y-%m-%d %H:%M:%S') if op.end_time else 'N/A'}\n\n"
            
            await query.edit_message_text(details_message, parse_mode='Markdown')

        elif query.data == 'scan_summary':
            summary = status_manager.get_summary()
            summary_message = f"""📊 *Detailed Scan Summary*

• Total Scan Operations: {summary['total']}
• Successfully Completed: {summary['completed']}
• Failed Operations: {summary['failed']}
• Operations In Progress: {summary['in_progress']}

*Performance Metrics:*
• Success Rate: {(summary['completed'] / summary['total'] * 100) if summary['total'] > 0 else 0:.2f}%
• Failure Rate: {(summary['failed'] / summary['total'] * 100) if summary['total'] > 0 else 0:.2f}%"""
            
            await query.edit_message_text(summary_message, parse_mode='Markdown')

        elif query.data == 'system_info':
            system_message = f"""🖥️ *System Information*

• Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Python Version: {sys.version.split()[0]}
• Active Tools: {len(self.cyber_toolkit.tm.tools)}
• Current Mode: Security Assessment
• Bot Uptime: {datetime.now() - self.start_time}"""
            
            await query.edit_message_text(system_message, parse_mode='Markdown')

        # Existing scan-related callbacks
        elif query.data == 'scan_cancel':
            self.active_scans.pop(query.message.chat_id, None)
            await query.edit_message_text("🚫 Scan cancelled!")

        elif query.data == 'scan_confirm':
            scan_info = self.active_scans.get(query.message.chat_id)
            if not scan_info:
                await query.edit_message_text("❌ Scan configuration not found!")
                return

            await query.edit_message_text("Scan started! You'll receive progress updates...")
            asyncio.create_task(
                self.execute_scan(query.message.chat_id, scan_info, context)
            )

    async def execute_scan(self, chat_id: int, scan_info: Dict[str, Any], context: ContextTypes.DEFAULT_TYPE) -> None:
        """Execute scan with real-time updates"""
        ui_manager = TelegramUIManager(context.bot, chat_id)
        self.cyber_toolkit.ui = ui_manager

        status_message = await context.bot.send_message(
            chat_id=chat_id,
            text="🚀 *Initializing Scan*\n\nPreparing tools...",
            parse_mode='Markdown'
        )

        try:
            # Prepare environment
            await ui_manager.send_progress("Setting up environment...")
            self.cyber_toolkit.prepare_environment(scan_info['tools'])

            # Update status
            await ui_manager.send_progress(
                f"Starting scan on `{scan_info['target']}`\n"
                f"Running {len(scan_info['tools'])} tools with {scan_info['workers']} workers"
            )

            # Execute tools
            results = self.cyber_toolkit.execute_tools(
                scan_info['tools'],
                scan_info['target'],
                scan_info['workers']
            )

            # Send results
            status_manager = ExecutionStatusManager()
            status_manager.load_status()
            summary = status_manager.get_summary()

            summary_message = f"""📊 *Scan Summary*:

- Total Operations: {summary['total']}
- Completed: {summary['completed']}
- Failed: {summary['failed']}
- In Progress: {summary['in_progress']}

👆 For more details, use /status command.

"""

            await context.bot.send_message(
                chat_id=chat_id,
                text=summary_message,
                parse_mode='Markdown'
            )


            # Send completion message
            await context.bot.send_message(
                chat_id=chat_id,
                text="✅ *Scan Completed*\nAll tools have finished execution.",
                parse_mode='Markdown'
            )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            line_number = exc_tb.tb_lineno
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ *Error During Scan*\n`{str(e)}`\nOccurred at line: {line_number}",
                parse_mode='Markdown'
            )

        finally:
            self.active_scans.pop(chat_id, None)

    async def scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /scan command"""
        if not context.args:
            usage_message = """⚠️ *Scan Usage:*

`/scan <target> [workers] [mode]`

*Examples:*
• `/scan example.com` - Scan with defaults
• `/scan example.com 4 all` - All tools
• `/scan example.com 2 tool1,tool2` - Specific tools

*Defaults:*
• Workers: 4
• Mode: all"""
            await update.message.reply_text(usage_message, parse_mode='Markdown')
            return

        target = context.args[0]
        workers = int(context.args[1]) if len(context.args) > 1 else 4
        mode = context.args[2] if len(context.args) > 2 else 'all'

        # Validate target
        if not target or ' ' in target:
            await update.message.reply_text("❌ *Error:* Invalid target format", parse_mode='Markdown')
            return

        # Prepare tools
        tools_input = [] if mode == 'all' else mode.split(',')
        tools_to_run = self.cyber_toolkit.validate_and_prepare_tools(tools_input)

        if not tools_to_run:
            await update.message.reply_text("❌ *Error:* No valid tools selected", parse_mode='Markdown')
            return

        # Store scan information
        chat_id = update.effective_chat.id
        self.active_scans[chat_id] = {
            'target': target,
            'tools': tools_to_run,
            'workers': workers
        }

        # Create confirmation keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ Start Scan", callback_data='scan_confirm'),
                InlineKeyboardButton("❌ Cancel", callback_data='scan_cancel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        confirm_message = f"""🎯 *Scan Configuration*

• Target: `{target}`
• Workers: {workers}
• Tools: {len(tools_to_run)}
• Mode: {mode}

*Selected Tools:*
{', '.join(t['name'] for t in tools_to_run)}

Please confirm to start the scan:"""

        await update.message.reply_text(
            confirm_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    def run(self) -> None:
        """Run the Telegram bot"""
        app = Application.builder().token(self.token).build()

        # Add command handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(CommandHandler("list", self.list_tools))
        app.add_handler(CommandHandler("scan", self.scan))
        app.add_handler(CallbackQueryHandler(self.button_callback))
        app.add_handler(CommandHandler("status", self.status))

        # Start the bot
        app.run_polling()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Replace with your bot token
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    bot = TelegramBot(BOT_TOKEN)
    bot.run()