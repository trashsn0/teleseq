import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import postage
import requests
import os

# Global variables
bot_token = None
logseq_abs_path = None
polling_interval = None
authorized_users = None
public = None
STOP_FLAG_PATH = '/tmp/bot_stop_flag'

def getConfig():
    global bot_token, logseq_abs_path, polling_interval, authorized_users, public

    flask_url = os.environ.get('FLASK_URL', 'http://localhost:7575')
    response = requests.get(f'{flask_url}/get_config')
    config = response.json()

    # Fetch the configuration from the database
    if config != {}:
        bot_token = config['bot_token']
        logseq_abs_path = config['logseq_abs_path']
        authorized_users = config['authorized_users']

        if authorized_users == 0 :
            public = True

    else:
        print("No configuration found. Please configure the bot.")
        exit(1)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    # Check if the username is allowed
    if not public and user.username not in authorized_users:
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
    if not public and user.username not in authorized_users:
        return
    await update.message.reply_text("Here are the available commands ∴ :\n\n - /log for adding under #log \n - Regular messages : new block in daily")

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    user = update.effective_user
    # Check if the username is allowed
    if not public and user.username not in authorized_users:
        return
    
    result = postage.newBlock(postage.getTodayJournalPath(logseq_abs_path),update.message.text_markdown)
    await update.message.reply_text(result)
    

def rebuild() -> None:
    """Start the bot."""
        
    # Fetch the configuration
    getConfig()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, post))


    application.run_polling(allowed_updates=Update.ALL_TYPES)

        
if __name__ == '__main__' :
    rebuild()

