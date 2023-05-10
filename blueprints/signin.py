from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from mongo import mongo
from crypto import crypto
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

    # Check credentials
    valid_credentials = True
    if username == "":
        valid_credentials = False
        flash("Username cannot be empty!", "error")

    # Check if username already exists
    success, reason = mongo.check_username(hash_username)
    if success:
        valid_credentials = False
        flash("This username is taken!", "error")
    elif reason != "":
        flash(reason, "error")
        return redirect(url_for("index"))
    
    # Validate password
    valid_psw, reason = psw_validation.validate(password)
    if not valid_psw:
        valid_credentials = False
        flash(reason, "error")
    
    # Render error if something is not valid
    if not valid_credentials:
        return redirect(url_for("signin.signin_get"))
    else:
        # Hash password and add user to mongo
        psw_hash = crypto.hash_str(password)
        success, reason = mongo.add_credentials(hash_username, psw_hash)
        if not success:
            flash(reason, "error")
            return redirect(url_for("index"))
        
        # Generate salt and save to mongo
        salt = os.urandom(16)
        salt_hash = crypto.hash_bytes(psw_hash + hash_username)
        success, reason = mongo.add_salt(salt_hash, salt)
        if not success:
            flash(reason, "error")
            return redirect(url_for("index"))
        
        # Derive key and add empty vault
        key = crypto.derive_key(password, salt)
        vault_data = json.dumps({})
        encrypted_vault = crypto.encrypt(key, vault_data)
        success, reason = mongo.add_vault(hash_username, encrypted_vault)

        if not success:
            flash(reason, "error")
            return redirect(url_for("index"))
        else:
            flash("User was created successfully!", "success")
            return redirect(url_for("index"))