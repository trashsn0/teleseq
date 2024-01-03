import subprocess
import atexit
import os
import signal
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


##################################################### GRACEFULL EXIT #####################################################
def cleanup() :
    stop_bot()

atexit.register(cleanup)

##################################################### FLASK AND DATABASE #################################################

app = Flask(__name__,static_folder="assets")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/teleseq.db'
db = SQLAlchemy(app)

class BotConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_token = db.Column(db.String(80), unique=True, nullable=False)
    authorized_users = db.Column(db.String(120), nullable=False)
    logseq_abs_path = db.Column(db.String(120), nullable=False)
    bot_state = db.Column(db.String(20), nullable=False, default='stopped')
    bot_pid = db.Column(db.Integer, nullable=True)


#################################################### BOT CONTROL AND STATE FUNCTIONS ######################################

def start_bot():
    bot_config = BotConfig.query.first()
    if bot_config.bot_state == 'stopped':
        bot_process = subprocess.Popen(['python', 'bot.py'])
        bot_config.bot_pid = bot_process.pid
        bot_config.bot_state = 'running'
        db.session.commit()
        return 'Bot started'
    else:
        return 'Bot is already running'

def stop_bot():
    with app.app_context() :
        bot_config = BotConfig.query.first()
        if not bot_config :
            return 'Configuration not found'
        if bot_config.bot_state == 'running':

            try :
                os.kill(bot_config.bot_pid, signal.SIGTERM)
                bot_config.bot_state = 'stopped'
                bot_config.bot_pid = None
                db.session.commit()
                return 'Bot stopped'
            except Exception as e :
                bot_config.bot_state = 'stopped'
                bot_config.bot_pid = None
                db.session.commit()
                print ("STOP CANCEL WROTE TO DB")
                return 'Bot stopped'
            
        else:
            return 'Bot is not running'

def bot_state():
    bot_config = BotConfig.query.first()
    return bot_config.bot_state


#################################################### GET CONFIG ROUTE #########################################################

@app.route('/get_config')
def get_config():
    config = BotConfig.query.first()
    if config:
        return dict(
                    bot_token = config.bot_token, 
                    authorized_users = config.authorized_users.split(',') if config.authorized_users else 0, 
                    logseq_abs_path = config.logseq_abs_path,
                    )
    else:
        return {}
    

#################################################### INDEX ROUTE #########################################################

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    warning = None
    success = None
    if request.method == 'POST':

        # NEW CONFIGURATION
        if 'config' in request.form :
            bot_token = request.form['bot_token']
            authorized_users = request.form['authorized_users']
            logseq_abs_path = request.form['logseq_abs_path']
            
            #Data validation
            if not bot_token or not logseq_abs_path:
                error = '❗ Missing Fields - token, logseq path and polling interval mandatory'

            if not authorized_users :
                warning = '⚠️ If you do not restrict to certain users, everyone will be able to access your logseq graph'

            if error is None :
                config = BotConfig.query.first()
                if config:
                    config.bot_token = bot_token
                    config.authorized_users = authorized_users
                    config.logseq_abs_path = logseq_abs_path

                    stop_bot()
                    start_bot()
                
                else:
                    new_config = BotConfig(bot_token=bot_token, authorized_users=authorized_users, logseq_abs_path=logseq_abs_path)
                    db.session.add(new_config)

                db.session.commit()
                success = 'All good'

            
            
        # BOT CONTROL BUTTONS
        if "start" in request.form :
            start_bot()
            success= "Your bot is starting..."
        elif "stop" in request.form :
            stop_bot()
            success = "Your bot is stopping..."


    config = BotConfig.query.first()
    result = {"error":error,"warning":warning,"success":success}

    if config :
        return render_template('index.html',page1=True, bot_token=config.bot_token, authorized_users=config.authorized_users.split(','), logseq_abs_path=config.logseq_abs_path, state=config.bot_state, result=result)
    else:
        return render_template('index.html',page1=True,result=result)
    

#################################################### HOWTO ROUTE #########################################################


@app.route("/howto")
def howto() :
    return render_template('howto.html',page2=True)


#################################################### MAIN INTERFACE #########################################################

def main() :
    try :
        with app.app_context() :
            db.create_all()
        app.run(debug=True,port=7575)
    except KeyboardInterrupt :
        stop_bot()


if __name__ == "__main__":  
    main()