from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from mongo import mongo
from crypto import crypto
from loguru import logger
import json

login = Blueprint('login', __name__,
        template_folder='templates')

@login.route("/login", methods=["GET"])
def login_get():
    if not session.get("name"):
        return render_template("login.html")
    else:
        return redirect(url_for("vaults.vaults_get"))

@login.route("/login", methods=["POST"])
def login_post():
    multidict = request.form
    credentials = multidict.to_dict(flat=False)
    username = credentials["username"][0]
    hash_username = crypto.hash_str(username)
    password = credentials["password"][0]
    logger.info(f"User '{username} tries to log in!'")
    # Check if username existss
    logger.info(f"Fetching username '{username}' from mongo")
    creds, reason = mongo.get_credentials(hash_username)
    if not creds:
        if reason == "":
            # Username doesn't exist
            logger.info(f"User '{username} doesn't exit!'")
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
            # Session is encrypted and client-side
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