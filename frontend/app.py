from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__,static_folder='assets')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///config.db'
app.config['SECRET_KEY'] = 'tunamayo'
db = SQLAlchemy(app)



class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_token = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    logseq_path = db.Column(db.String(200), nullable=False)
    
with app.app_context() :
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bot_token = request.form['bot_token']
        username = request.form['username']
        logseq_path = request.form['logseq_path']
        new_config = Config(bot_token=bot_token, username=username, logseq_path=logseq_path)
        try:
            db.session.add(new_config)
            db.session.commit()
            flash('Configuration saved successfully!', 'success')
            return redirect(url_for('index'))
        except:
            flash('There was an issue saving your configuration', 'error')
    else:
        config = Config.query.first()
        return render_template('index.html', config=config,page1=True)
    

@app.route("/howto")
def howto() :
    return render_template('howto.html',page2=True)

if __name__ == "__main__":
    app.run(port=8888,debug=True)