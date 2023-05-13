from flask import Blueprint, redirect, render_template, request, session, url_for, flash, abort, current_app
from utils.mongo import mongo
from utils.crypto import crypto
from loguru import logger
import json
import requests
import os

login = Blueprint('login', __name__,
        template_folder='templates')

RECAPTCHA_VERIFY_URL = os.getenv("RECAPTCHA_VERIFY_URL")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")

@login.route("/login", methods=["GET"])
def login_get():
    if not session.get("name"):
        return render_template("login.html", site_key = RECAPTCHA_SITE_KEY)
    else:
        return redirect(url_for("vaults.vaults_get"))

@login.route("/login", methods=["POST"])
def login_post():
    # Capthca is disabled whent testing
    if not current_app.config["TESTING"]:
        # Verify captcha
        secret_response = request.form["g-recaptcha-response"]
        verify_response = requests.post(
            url=f"{RECAPTCHA_VERIFY_URL}?secret={RECAPTCHA_SECRET_KEY}&response={secret_response}").json()
        # Check success and score 
        # 0.5 threshold is default recommended in reCaptcha docs
        if verify_response["success"] == False:
            logger.error("Unable to verify recaptcha!")
            abort(401)
        elif verify_response["score"] < 0.5:
            logger.error("ReCaptcha score is under 0.5!")
            abort(401)
    
    credentials = request.form.to_dict(flat=False)
    username = credentials["username"][0]
    hash_username = crypto.hash_str(username)
    password = credentials["password"][0]
    logger.info(f"User '{username}' tries to log in!'")
    # Check if username existss
    logger.info(f"Fetching username '{username}' from mongo")
    creds, reason = mongo.get_credentials(hash_username)
    if not creds:
        if reason == "":
            # Username doesn't exist
            logger.info(f"User '{username}' doesn't exit!'")
            flash("Given username doesn't exist!", "error")
        else:
            # Mongo error
            flash(reason, "error")
        return redirect(url_for("login.login_get"))
    else:
        logger.info(f"User '{username}' provided right credentials!")

        # Hash password to match with stored password
        psw_hash = crypto.hash_str(password)
        if creds["psw"] == psw_hash:
            # Get encrypted vault from mongo
            logger.info(f"Fetching vaults for user '{username}'")
            encrypted_vault, reason = mongo.get_vault(hash_username)
            if not encrypted_vault:
                flash(reason, "error")
                return redirect(url_for("login.login_get"))
            
            # Hash username and password and fetch salt
            salt_hash = crypto.hash_bytes(psw_hash + hash_username)
            logger.info(f"Fetching salt for user '{username}'")
            salt, reason = mongo.get_salt(salt_hash)
            if not salt:
                flash(reason, "error")
                return redirect(url_for("login.login_get"))
            else:
                salt = salt["salt"]
            
            # Derive key
            key = crypto.derive_key(password, salt)
            decrypted_vault = crypto.decrypt(key, encrypted_vault["vault"])

            # Add session details
            # Session is encrypted and server-side
            session["name"] = hash_username
            session["plaintxt_name"] = username
            session["vault"] = json.loads(decrypted_vault)
            session["key"] = key
            session.modified = True

            logger.info(f"User '{username}' has logged in!")
            flash("Logged In!", "success")
            return redirect(url_for("vaults.vaults_get"))
        else:
            logger.warning(f"Wrong password provided for user '{username}'")
            flash("Password is incorrect!", "error")
            return redirect(url_for("login.login_get"))