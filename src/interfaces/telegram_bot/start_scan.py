import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from src.interfaces.telegram_bot import ContextTypes



async def scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /scan command, validate input, and prompt the user for confirmation."""
        if not context.args:
            usage_message = (
                "⚠️ *Scan Usage:*\n\n"
                "`/scan <target> [workers] [mode]`\n\n"
                "💡 *Examples:*\n"
                "🔹 `/scan example.com` – Scan with defaults\n"
                "🔹 `/scan example.com 4 all` – Run all tools\n"
                "🔹 `/scan example.com 2 tool1,tool2` – Run specific tools\n\n"
                "📌 *Defaults:* Workers: 4 | Mode: all"
            )
            await update.message.reply_text(usage_message, parse_mode="Markdown")
            return

        target = context.args[0]
        workers = int(context.args[1]) if len(context.args) > 1 and context.args[1].isdigit() else 4
        mode = context.args[2] if len(context.args) > 2 else "all"

        if not target or " " in target:
            await update.message.reply_text("❌ *Error:* Invalid target format", parse_mode="Markdown")
            return

        tools_input = [] if mode.lower() == "all" else mode.split(",")
        # نفترض وجود دالة validate_and_prepare_tools ضمن cyber_toolkit
        tools_to_run = self.cyber_toolkit.validate_and_prepare_tools(tools_input)

        if not tools_to_run:
            await update.message.reply_text("❌ *Error:* No valid tools selected", parse_mode="Markdown")
            return

        chat_id = update.effective_chat.id
        self.active_scans = {}  # تأكد من تعريفه مسبقًا أو استخدم خاصية مناسبة
        self.active_scans[chat_id] = {
            "target": target,
            "tools": tools_to_run,
            "workers": workers,
        }

        keyboard = [
            [
                InlineKeyboardButton("✅ Start Scan", callback_data="scan_confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data="scan_cancel"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        confirm_message = (
            "🎯 *Scan Configuration*\n\n"
            f"🔹 *Target:* `{target}`\n"
            f"🔹 *Workers:* {workers}\n"
            f"🔹 *Tools:* {len(tools_to_run)}\n"
            f"🔹 *Mode:* {mode}\n\n"
            "🛠️ *Selected Tools:*\n"
            f"{', '.join(t['name'] for t in tools_to_run)}\n\n"
            "Please confirm to start the scan:"
        )
        await update.message.reply_text(
            confirm_message, reply_markup=reply_markup, parse_mode="Markdown"
        )

    async def start_scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        بعد تأكيد المستخدم لبدء الفحص (scan_confirm) يتم استدعاء هذه الدالة،
        حيث يتم بدء الفحص وإرسال رسالة للمستخدم تحتوي على operations_now
        وتحديث محتواها تلقائيًا.
        """
        chat_id = update.effective_chat.id

        # وضع علامة أن عملية الفحص بدأت
        self.scanning_active = True

        # إرسال رسالة أولية للمستخدم تحتوي على operations_now
        sent_message = await update.message.reply_text(
            f"🚀 *Scan Started*\nCurrent operations: {self.operations_now}",
            parse_mode="Markdown"
        )

        # بدء مهمة لتحديث الرسالة تلقائياً
        self.scan_update_task = asyncio.create_task(
            self._update_scan_status(context, chat_id, sent_message.message_id)
        )

        # هنا يمكنك بدء عملية الفحص الحقيقية، وعند تحديث self.operations_now سيتم تحديث الرسالة تلقائياً.
        # على سبيل المثال:
        # await self.run_scan(target, tools_to_run, workers)

        # عند انتهاء الفحص، تأكد من إيقاف تحديث الرسالة:
        # self.scanning_active = False
        # إذا لزم الأمر، قم بإلغاء المهمة:
        # if self.scan_update_task:
        #     self.scan_update_task.cancel()

    async def _update_scan_status(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> None:
        """
        مهمة غير متزامنة تقوم بتحديث الرسالة التي تحتوي على operations_now كل ثانية
        طالما أن عملية الفحص نشطة.
        """
        try:
            while self.scanning_active:
                new_text = f"🚀 *Scan in Progress*\nCurrent operations: {self.operations_now}"
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=new_text,
                    parse_mode="Markdown"
                )
                await asyncio.sleep(1)  # تحديث كل ثانية
        except asyncio.CancelledError:
            # عند إلغاء المهمة، يمكنك إرسال رسالة نهائية للمستخدم إذا رغبت
            pass