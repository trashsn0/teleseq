import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__,static_folder="assets")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/teleseq.db'
db = SQLAlchemy(app)

class BotConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_token = db.Column(db.String(80), unique=True, nullable=False)
    authorized_users = db.Column(db.String(120), nullable=False)
    logseq_abs_path = db.Column(db.String(120), nullable=False)


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
    

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    warning = None
    success = None
    if request.method == 'POST':
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
            else:
                new_config = BotConfig(bot_token=bot_token, authorized_users=authorized_users, logseq_abs_path=logseq_abs_path)
                db.session.add(new_config)

            db.session.commit()
            success = 'All good'
            

    config = BotConfig.query.first()
    result = {"error":error,"warning":warning,"success":success}

    if config :        
        return render_template('index.html',page1=True, bot_token=config.bot_token, authorized_users=config.authorized_users.split(','), logseq_abs_path=config.logseq_abs_path, result=result)
    else:
        return render_template('index.html',page1=True,result=result)
    

@app.route("/howto")
def howto() :
    return render_template('howto.html',page2=True)

if __name__ == "__main__":
    with app.app_context() :
        db.create_all()
    app.run(port=8888,debug=True)