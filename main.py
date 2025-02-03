#from src.interfaces.CLI_parser import CLIInput
from src.interfaces.telegram_bot import TelegramBot

if __name__ == "__main__":
    BOT_TOKEN = "8067500091:AAGc9efhwdEP3X9S09vJt6IXN0BpxolSYg0"
    # Configure logging


    bot = TelegramBot(BOT_TOKEN)
    bot.run()