import bot  
import os

STOP_FLAG_PATH = '/tmp/bot_stop_flag'

def stop_bot():
    open(STOP_FLAG_PATH, 'a').close()  # create the flag file

def start_bot():
    bot.rebuild()



def restart_bot():
    stop_bot()
    start_bot()
    

# To restart the bot, simply call restart_bot()
if __name__ == '__main__' :
    stop_bot()
