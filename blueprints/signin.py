from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from mongo import mongo
from crypto import crypto
from loguru import logger
import psw_validation
import json
import os

signin = Blueprint('signin', __name__,
        template_folder='templates')

@signin.route("/signin", methods=["GET"])
def signin_get():
    """
    Render Sign In page
    """
    if not session.get("name"):
        return render_template("signin.html")
    else:
        return redirect(url_for("vaults.vaults_get"))

@signin.route("/signin", methods=["POST"])
def signin_post():
    """
    Handle POST methods for sign ins.
    """
    credentials = request.form.to_dict(flat=False)
    username = credentials["username"][0]
    password = credentials["password"][0]
    hash_username = crypto.hash_str(username)

    logger.info(f"Trying to create user '{username}'!")

    # Check credentials
    valid_credentials = True
    if username == "":
        logger.warning(f"Invalid username '{username}' provided!")
        flash("Username cannot be empty!", "error")
        return redirect(url_for("signin.signin_get"))
    
    # Check if username already exists
    success, reason = mongo.get_credentials(hash_username)
    if success:
        logger.warning(f"User '{username} already exists!'")
        valid_credentials = False
        flash("This username is taken!", "error")
    elif reason != "":
        flash(reason, "error")
        return redirect(url_for("index"))
    
    # Validate password
    valid_psw, reason = psw_validation.validate(password)
    if not valid_psw:
        logger.warning(f"Invalid password provided!")
        valid_credentials = False
        flash(reason, "error")
    
    # Render error if something is not valid
    if not valid_credentials:
        return redirect(url_for("signin.signin_get"))
    else:
        logger.info(f"Creating user '{username}'!")
        # Hash password and add user to mongo
        psw_hash = crypto.hash_str(password)
        logger.info(f"Adding user '{username}' to mongo!")
        success, reason = mongo.add_credentials(hash_username, psw_hash)
        if not success:
            flash(reason, "error")
            return redirect(url_for("index"))
        
        # Generate salt and save to mongo
        salt = os.urandom(16)
        salt_hash = crypto.hash_bytes(psw_hash + hash_username)
        logger.info(f"Adding salt for user '{username}' to mongo!")
        success, reason = mongo.add_salt(salt_hash, salt)
        if not success:
            flash(reason, "error")
            return redirect(url_for("index"))
        
        # Derive key and add empty vault
        key = crypto.derive_key(password, salt)
        vault_data = json.dumps({})
        encrypted_vault = crypto.encrypt(key, vault_data)
        logger.info(f"Adding vault for user '{username}' to mongo!")
        success, reason = mongo.add_vault(hash_username, encrypted_vault)

        if not success:
            flash(reason, "error")
            return redirect(url_for("index"))
        else:
            logger.info(f"User '{username}' created successfully!")
            flash("User was created successfully!", "success")
            return redirect(url_for("index"))