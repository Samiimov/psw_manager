from flask import Flask, redirect, render_template, session, url_for
from flask_session import Session
from flask_wtf import CSRFProtect
from blueprints.signin import signin
from blueprints.login import login
from blueprints.vaults  import vaults
from loguru import logger
from mongo import mongo
from crypto import crypto
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    # Used for enrypting sessions
    app.config["SECRET_KEY"] = os.urandom(16)
    app.config["SESSION_TYPE"] = "filesystem"
    # Logs out after 10 minutes
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
    load_dotenv()
    # Fetch the value of LOG_ENCRYPTION_KEY from the environment
    log_encryption_key = os.getenv("LOG_ENCRYPTION_KEY")

    # Check if the environment variable exists
    if log_encryption_key is None:
        logger.info("LOG_ENCRYPTION_KEY is not set in the .env file.")
    
    # Logger
    date_time = datetime.strftime(datetime.now(), "%d_%m_%Y")
    if log_encryption_key is not None:
        try:
            crypto.set_logging_cipher(log_encryption_key)
            logger.add(f"logs/logfile_{date_time}_encrypted.log", format=crypto.encrypted_formatter)
        except ValueError as e:
            logger.error(e)
            logger.info("Existing!")
            sys.exit()
    else:
        logger.add(f"logs/logfile_{date_time}.log")

    logger.info("Starting!")
    mongo_connection = mongo.create_connection()
    mongo.initialize_mongo()
    app.run(host='localhost', port=5001, debug=True, ssl_context='adhoc')