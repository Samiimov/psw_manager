from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from utils.mongo import mongo
from utils.crypto import crypto
import utils.psw_validation as psw_validation
import json
import copy
from loguru import logger

vaults = Blueprint('vaults', __name__,
            template_folder='templates')

@vaults.route("/vaults", methods=["GET"])
def vaults_get():
    if not session.get("name"):
        return redirect(url_for("index"))
    else:
        return render_template("vaults.html", vaults=list(session["vault"].keys()))
    
@vaults.route("/vaults/<vault_name>", methods=["GET"])
def open_vault(vault_name):
    if not session.get("name"):
        return redirect(url_for("index"))
    else:
        name = session.get("plaintxt_name")
        logger.info(f"User '{name}' opened vault '{vault_name}'")
        return render_template("show_vault.html", vault_items=session["vault"][vault_name], vault_name=vault_name)

@vaults.route("/create_vault", methods=["GET"])
def create_vault_get():
    if not session.get("name"):
        return redirect(url_for("index"))
    else:
        return render_template("create_vault.html")

@vaults.route("/create_vault", methods=["POST"])
def create_vault_post():
    if not session.get("name"):
        return redirect(url_for("index"))
    else:
        name = session.get("plaintxt_name")
        form = request.form.to_dict(flat=False)
        vault_name = form["Name"][0]
        logger.info(f"User '{name}' tries to create vault '{vault_name}'")
        # Check that provided vault name is valid
        if vault_name in session["vault"]:
            logger.warning(f"User error with user '{name}': Vault named '{vault_name}' already exists!")
            flash(f"Vault named '{vault_name}' already exists!", "error")
            return redirect(url_for("vaults.create_vault_get"))
        elif vault_name == "" or vault_name[-1] == " ":
            logger.warning(f"User error with user '{name}': Vault name can't be empty or end in space!")
            flash("Vault name can't be empty or end in space!", "error")
            return redirect(url_for("vaults.create_vault_get"))
        else:
            # Encrypt vaults and save to mongo 
            session["vault"][vault_name] = {}
            encrypted_vault = crypto.encrypt(session["key"], json.dumps(session["vault"]))
            logger.info(f"Creating vault '{vault_name}' for user '{name}' in mongo")
            sucess, reason = mongo.update_vault(session["name"], encrypted_vault)
            if not sucess:
                flash(reason, "error")
                return redirect(url_for("vaults.vaults_get"))
            else:
                logger.info(f"Vault '{vault_name}' created for user '{name}'")
                flash("Vault created sucessfully!", "success")
                session.modified = True
                return redirect(url_for("vaults.vaults_get"))
        
@vaults.route("/update_vault/<vault_name>", methods=["POST"])
def update_vault_post(vault_name):
    if not session.get("name"):
        return redirect(url_for("index"))
    else:
        name = session.get("plaintxt_name")
        logger.info(f"Updating vault '{vault_name}' for user '{name}'")
        # Create backup variable of current vault        
        vault_backup = copy.deepcopy(session["vault"][vault_name])

        form = request.form.to_dict(flat=False)
        try:
            vault_item_keys = form["Name"]
            vault_item_values = form["Password"]
        except KeyError:
            # Removes all items
            vault_item_keys = []
            vault_item_values = []
        
        # Remove missing keys from current vault
        # -> means that these keys have been removed via UI
        for i in list(session["vault"][vault_name].keys()):
            if not i in vault_item_keys:
                del session["vault"][vault_name][i]
        
        unvalid_passwords = False
        # Check provided password for invalid ones
        for index, key in enumerate(vault_item_keys):
            password = vault_item_values[index]
            is_valid_password, reason = psw_validation.validate(password)
            if is_valid_password:
                session["vault"][vault_name][key] = vault_item_values[index]
            else:
                unvalid_passwords = True
                logger.error(f"Could not save '{key}': {reason}", "error")
                flash(f"Could not save '{key}': {reason}", "error")
        session.modified = True
        encrypted_vault = crypto.encrypt(session["key"], json.dumps(session["vault"]))
        logger.info(f"Updating vault '{vault_name}' for user '{name}' in mongo!")
        # Sabve vault to mongo
        success, reason = mongo.update_vault(session["name"], encrypted_vault)
        if not success:
            # If saving to mongo doesn't work
            # -> bring back vault from vault_backup variables
            session["vault"][vault_name] = vault_backup
            flash(reason, "error")
            return redirect(f"/vaults/{vault_name}")
        else:   
            logger.info(f"Updated vault '{vault_name}' for user '{name}'")
            if unvalid_passwords:
                flash("Other items saved successfully", "success")
            else:
                flash("Items saved succesfully!", "success")
            return redirect(f"/vaults/{vault_name}")

@vaults.route("/remove_vault/<vault_name>", methods=["POST"])
def remove_vault_post(vault_name):
    if not session.get("name"):
        return redirect(url_for("index"))
    else:
        # Get plaintext name from session
        name = session.get("plaintxt_name")
        logger.info(f"Removing vault '{vault_name}' from user '{name}'")
        try:
            # Try to delete vault from the current vaults
            vault_backup = copy.deepcopy(session["vault"][vault_name])
            del session["vault"][vault_name]
        except KeyError:
            flash("Given vault doesn't exist!", "error")
            return redirect(url_for("vaults.vaults_get"))
        session.modified = True
        # Encrypt new vault
        encrypted_vault = crypto.encrypt(session["key"], json.dumps(session["vault"]))
        logger.info(f"Updating vault '{vault_name}' for user '{name}'")
        # Save vault to mongo
        success, reason = mongo.update_vault(session["name"], encrypted_vault)
        if not success:
            # If saving to mongo doesn't work
            # -> bring back vault from vault_backup variables
            logger.error(reason)
            session["vault"][vault_name] = vault_backup
            flash(reason, "error")
            return redirect(url_for("vaults.vaults_get"))
        else:
            logger.info(f"Removed vault '{vault_name}' from user '{name}'")
            flash("Vault removed succesfully!", "success")
            return redirect(url_for("vaults.vaults_get"))