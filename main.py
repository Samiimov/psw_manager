from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_session import Session
from flask_wtf import CSRFProtect
from blueprints.signin import signin
from blueprints.login import login
from blueprints.vaults  import vaults
from mongo import mongo
import os

def create_app():
    app = Flask(__name__)
    # Used for enrypting sessions
    app.config["SECRET_KEY"] = os.urandom(16)
    app.config["SESSION_TYPE"] = "filesystem"
    # Set sessions lifetime to 30 minutes 
    # -> Logs out after 10 minutes of inactivity
    app.config["PERMANENT_SESSION_LIFETIME"] = 600
    # The session will be deleted when the user closes the browser.
    app.config["SESSION_PERMANENT"] = False
    return app

sess = Session()
app = create_app()
app.register_blueprint(login)
app.register_blueprint(signin)
app.register_blueprint(vaults)
csrf = CSRFProtect(app)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/', methods=["GET"])
def index():
    if not session.get("name"):
        return render_template("index.html")
    else:
        return redirect(url_for("vaults.vaults_get"))
    
if __name__ == '__main__':
    mongo_connection = mongo.create_connection()
    mongo.initialize_mongo()
    app.run(host='localhost', port=5001, debug=True)