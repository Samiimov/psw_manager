from flask import Flask, redirect, render_template, session, url_for
from flask_session import Session
from flask_wtf import CSRFProtect
from blueprints.signin import signin
from blueprints.login import login
from blueprints.vaults  import vaults
from loguru import logger
from utils.mongo import mongo
from utils.crypto import crypto
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

# Create app and register blueprints
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
    # Fetch the enviroment values from .env file
    load_dotenv()
    # Possible encryption key for log files
    log_encryption_key = os.getenv("LOG_ENCRYPTION_KEY")
    # ReCaptcha variavbles
    recaptcha_secret = os.getenv("RECAPTCHA_SECRET_KEY")
    recaptcha_site_key = os.getenv("RECAPTCHA_SITE_KEY")
    recaptcha_verify_url = os.getenv("RECAPTCHA_VERIFY_URL")
    # Mongo variables
    mongo_url = os.getenv("MONGO_URL")
    try:
        mongo_port = int(os.getenv("MONGO_PORT"))
    except TypeError:
        logger.error("Mongo port must be interger!")
        sys.exit()

    # Check if the environment variable exists
    if log_encryption_key is None:
        logger.warning("LOG_ENCRYPTION_KEY is not set in the .env file. Logs will not be encrypted!")
    
    # Logger
    date_time = datetime.strftime(datetime.now(), "%d_%m_%Y")
    if log_encryption_key is not None:
        try:
            crypto.set_logging_cipher(log_encryption_key)
            logger.add(f"logs/logfile_{date_time}_encrypted.log", 
                       format=crypto.encrypted_formatter)
        except ValueError as e:
            logger.error(e)
            logger.info("Existing!")
            sys.exit()
    else:
        logger.add(f"logs/logfile_{date_time}.log")

    # Check that recaptcha secret was given
    if not recaptcha_secret:
        logger.error("reCaptcha secret was not provided. Set it in .env file with key 'RECAPTCHA_SECRET_KEY'")
        sys.exit()
    if not recaptcha_site_key:
        logger.error("reCaptcha site key was not provided. Set it in .env file with key 'RECAPTCHA_SITE_KEY'")
        sys.exit()
    if not recaptcha_verify_url:
        logger.error("reCaptcha verification url was not provided. Set it in .env file with key 'RECAPTCHA_VERIFY_URL'")
        sys.exit()

    # Check that mongo variables were given
    if not mongo_url:
        logger.error("Mongo url was not provided. Set it in .env file with key 'MONGO_URL'")
        sys.exit()
    if not mongo_port:
        logger.error("Mongo port was not provided. Set it in .env file with key 'MONGO_PORT'")
        sys.exit()
    
    logger.info("Starting!")
    mongo_connection = mongo.create_connection()
    app.run(host='localhost', port=5001, debug=True, ssl_context='adhoc')