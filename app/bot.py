import logging
from app import BotConfig
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Fetch the configuration from the database
config = BotConfig.query.first()
if config:
    bot_token = config.bot_token
    authorized_users = config.authorized_users.split(',')
else:
    print("No configuration found. Please configure the bot.")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    # Check if the username is allowed
    if user.username not in authorized_users:
        await update.message.reply_html(
            rf"Hi {user.mention_html()}! Unfortunatly, this is a private TeleSeq bot and you are not authorized. Check https://github.com/trashsn0/teleseq to make your own.",
            reply_markup=ForceReply(selective=True)
        )
        return
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    # Check if the username is allowed
    if user.username not in authorized_users:
        return
    await update.message.reply_text("Here are the available commands ∴ :\n\n - /log for adding under #log \n - Regular messages : new block in daily")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    user = update.effective_user
    # Check if the username is allowed
    if user.username not in authorized_users:
        return
    await update.message.reply_text(update.message.text)

def rebuild() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    rebuild()
