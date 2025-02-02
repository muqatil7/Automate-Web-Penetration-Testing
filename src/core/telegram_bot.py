import logging
from abc import ABC, abstractmethod
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, filters

# Define conversation states
SET_TARGET, SET_WORKERS, SET_TOOLS = range(3)

class InputStrategy(ABC):
    @abstractmethod
    def get_parameters(self):
        pass

class TelegramInput(InputStrategy):
    def __init__(self, token):
        self.token = token
        self.parameters = {}  # معطيات الأداة ستخزن هنا
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.setup_handlers()

    def setup_handlers(self):
        # ConversationHandler لإدارة سير المحادثة
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                SET_TARGET: [MessageHandler(filters.text & ~filters.command, self.set_target)],
                SET_WORKERS: [MessageHandler(filters.text & ~filters.command, self.set_workers)],
                SET_TOOLS: [MessageHandler(filters.text & ~filters.command, self.set_tools)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        self.dispatcher.add_handler(conv_handler)
        # إضافة أوامر إضافية
        self.dispatcher.add_handler(CommandHandler('list_tools', self.list_tools))
        self.dispatcher.add_handler(CommandHandler('run', self.run_command))

    # أمر /start: يبدأ المحادثة ويطلب من المستخدم إدخال الهدف (Target)
    def start(self, update, context):
        update.message.reply_text("Welcome to the Cybersecurity Toolkit Bot.\nPlease enter the target URL or IP:")
        return SET_TARGET

    # يقوم بتعيين الهدف (Target) المُدخل
    def set_target(self, update, context):
        self.parameters['target'] = update.message.text.strip()
        update.message.reply_text(
            f"Target set to: {self.parameters['target']}.\nPlease enter the number of parallel workers (default is 4):"
        )
        return SET_WORKERS

    # يقوم بتعيين عدد العمال (workers)
    def set_workers(self, update, context):
        try:
            workers = int(update.message.text.strip())
        except ValueError:
            update.message.reply_text("Please enter a valid integer for workers:")
            return SET_WORKERS
        self.parameters['workers'] = workers
        update.message.reply_text(
            f"Workers set to: {workers}.\nPlease enter the tools to run separated by space or type 'all' to run all tools:"
        )
        return SET_TOOLS

    # يقوم بتعيين الأدوات المطلوبة للتنفيذ
    def set_tools(self, update, context):
        tools_input = update.message.text.strip()
        if tools_input.lower() == 'all':
            self.parameters['all_tools'] = True
            self.parameters['tools'] = []
        else:
            self.parameters['tools'] = tools_input.split()
            self.parameters['all_tools'] = False
        update.message.reply_text("Parameters have been set. Type /run to start the toolkit or /cancel to exit.")
        return ConversationHandler.END

    # أمر /list_tools: لعرض قائمة الأدوات المتوفرة
    def list_tools(self, update, context):
        # هنا يمكن دمج الكود مع مدير الأدوات (Tool Manager)
        # سنستخدم قائمة افتراضية للتوضيح
        available_tools = ['tool1', 'tool2', 'tool3']
        tools_str = "\n".join(available_tools)
        update.message.reply_text("Available tools:\n" + tools_str)

    # أمر /run: يقوم بتأكيد المعطيات ومن ثم يمكن ربطه بمنطق تنفيذ الأداة
    def run_command(self, update, context):
        if 'target' not in self.parameters:
            update.message.reply_text("Target is not set. Please use /start to begin.")
            return
        # إذا لم يُحدد عدد العمال، يتم تعيين القيمة الافتراضية
        if 'workers' not in self.parameters:
            self.parameters['workers'] = 4
        update.message.reply_text("Running toolkit with parameters:\n" + str(self.parameters))
        # هنا يمكن استدعاء منطق التشغيل الرئيسي للأداة (مثلاً CyberToolkit.run)
        # يمكنك استخدام المعطيات self.parameters في منطق التطبيق الرئيسي

    # أمر /cancel: لإلغاء العملية
    def cancel(self, update, context):
        update.message.reply_text("Operation cancelled.")
        return ConversationHandler.END

    # دالة get_parameters تقوم بتشغيل البوت وتبقى تعمل حتى يتم إنهاؤها
    def get_parameters(self):
        logging.info("Starting Telegram bot for input collection.")
        self.updater.start_polling()
        print("Telegram Bot is running. Please set parameters via Telegram.")
        # استخدام idle() يجعل البوت يعمل بشكل مستمر حتى يتم إيقافه يدويًا
        self.updater.idle()
        return self.parameters

# Example usage:
if __name__ == "__main__":
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram bot token.
    TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    telegram_input = TelegramInput(TELEGRAM_BOT_TOKEN)
    # get_parameters ستعمل وتبقى في انتظار تفاعل المستخدم عبر Telegram
    parameters = telegram_input.get_parameters()
    print("Parameters received:", parameters)
