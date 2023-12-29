from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__,static_folder="assets")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class BotConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_token = db.Column(db.String(80), unique=True, nullable=False)
    authorized_users = db.Column(db.String(120), nullable=False)
    logseq_abs_path = db.Column(db.String(120), nullable=False)
    polling_interval = db.Column(db.Integer, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    warning = None
    success = None
    if request.method == 'POST':
        bot_token = request.form['bot_token']
        authorized_users = request.form['authorized_users']
        logseq_abs_path = request.form['logseq_abs_path']
        polling_interval = request.form['polling_interval']
        
        #Data validation
        if not bot_token or not logseq_abs_path or not polling_interval:
            error = '❗ Missing Fields - token, logseq path and polling interval mandatory'

        if not authorized_users :
            warning = '⚠️ If you do not restrict to certain users, everyone will be able to access your logseq graph'

        if error is None :
            config = BotConfig.query.first()
            if config:
                config.bot_token = bot_token
                config.authorized_users = authorized_users
                config.logseq_abs_path = logseq_abs_path
                config.polling_interval = polling_interval
            else:
                new_config = BotConfig(bot_token=bot_token, authorized_users=authorized_users, logseq_abs_path=logseq_abs_path, polling_interval=polling_interval)
                db.session.add(new_config)

            db.session.commit()
            success = 'All good'

            # Here you would add the code to restart your bot

    config = BotConfig.query.first()
   

    if config :
        result = {"error":error,"warning":warning,"success":success}
        return render_template('index.html',page1=True, bot_token=config.bot_token, authorized_users=config.authorized_users.split(','), logseq_abs_path=config.logseq_abs_path, polling_interval=config.polling_interval, result=result)
    else:
        return render_template('index.html',page1=True)
    

@app.route("/howto")
def howto() :
    return render_template('howto.html',page2=True)

if __name__ == "__main__":
    with app.app_context() :
        db.create_all()
    app.run(port=8888,debug=True)