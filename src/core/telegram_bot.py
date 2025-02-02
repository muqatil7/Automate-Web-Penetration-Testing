import asyncio
import logging
from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters

# إعداد سجل الأحداث
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# تعريف حالات المحادثة
SET_TARGET, SET_WORKERS, SET_TOOLS = range(3)

class InputStrategy(ABC):
    @abstractmethod
    async def get_parameters(self):
        pass

class TelegramInput(InputStrategy):
    def __init__(self, token):
        self.token = token
        self.parameters = {}  # معطيات الأداة ستُخزَّن هنا
        self.app = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        # إعداد ConversationHandler لإدارة المحادثة
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                SET_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.set_target)],
                SET_WORKERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.set_workers)],
                SET_TOOLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.set_tools)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        # إضافة المعالجات إلى التطبيق
        self.app.add_handler(conv_handler)
        self.app.add_handler(CommandHandler('list_tools', self.list_tools))
        self.app.add_handler(CommandHandler('run', self.run_command))

    async def start(self, update: Update, context: CallbackContext) -> int:
        await update.message.reply_text("Welcome to the Cybersecurity Toolkit Bot.\nPlease enter the target URL or IP:")
        return SET_TARGET

    async def set_target(self, update: Update, context: CallbackContext) -> int:
        self.parameters['target'] = update.message.text.strip()
        await update.message.reply_text(
            f"Target set to: {self.parameters['target']}.\nPlease enter the number of parallel workers (default is 4):"
        )
        return SET_WORKERS

    async def set_workers(self, update: Update, context: CallbackContext) -> int:
        try:
            workers = int(update.message.text.strip())
        except ValueError:
            await update.message.reply_text("Please enter a valid integer for workers:")
            return SET_WORKERS
        self.parameters['workers'] = workers
        await update.message.reply_text(
            f"Workers set to: {workers}.\nPlease enter the tools to run separated by space or type 'all' to run all tools:"
        )
        return SET_TOOLS

    async def set_tools(self, update: Update, context: CallbackContext) -> int:
        tools_input = update.message.text.strip()
        if tools_input.lower() == 'all':
            self.parameters['all_tools'] = True
            self.parameters['tools'] = []
        else:
            self.parameters['tools'] = tools_input.split()
            self.parameters['all_tools'] = False
        await update.message.reply_text("Parameters have been set. Type /run to start the toolkit or /cancel to exit.")
        return ConversationHandler.END

    async def list_tools(self, update: Update, context: CallbackContext):
        available_tools = ['tool1', 'tool2', 'tool3']
        tools_str = "\n".join(available_tools)
        await update.message.reply_text(f"Available tools:\n{tools_str}")

    async def run_command(self, update: Update, context: CallbackContext):
        if 'target' not in self.parameters:
            await update.message.reply_text("Target is not set. Please use /start to begin.")
            return
        if 'workers' not in self.parameters:
            self.parameters['workers'] = 4
        await update.message.reply_text(f"Running toolkit with parameters:\n{self.parameters}")
        # يمكن استدعاء الوظائف الخاصة بتنفيذ الأداة هنا

    async def cancel(self, update: Update, context: CallbackContext) -> int:
        await update.message.reply_text("Operation cancelled.")
        return ConversationHandler.END

    async def get_parameters(self):
        logging.info("Starting Telegram bot for input collection.")
        print("Telegram Bot is running. Please set parameters via Telegram.")
        await self.app.run_polling()

# تشغيل البوت
if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = "8067500091:AAGc9efhwdEP3X9S09vJt6IXN0BpxolSYg0"
    telegram_input = TelegramInput(TELEGRAM_BOT_TOKEN)
    parameters = asyncio.run(telegram_input.get_parameters())
    print("Parameters received:", parameters)
