from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from mongo import mongo
from crypto import crypto
import psw_validation
import json
import copy

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
        form = request.form.to_dict(flat=False)
        vault_name = form["Name"][0]
        if vault_name in session["vault"]:
            flash(f"Vault named '{vault_name}' already exists!", "error")
            return redirect(url_for("vaults.create_vault_get"))
        elif vault_name == "" or vault_name[-1] == " ":
            flash("Vault name can't be empty or end in space!", "error")
            return redirect(url_for("vaults.create_vault_get"))
        else:
            session["vault"][vault_name] = {}
            encrypted_vault = crypto.encrypt(session["key"], json.dumps(session["vault"]))
            sucess, reason = mongo.update_vault(session["name"], encrypted_vault)
            if not sucess:
                flash(reason, "error")
                return redirect(url_for("vaults.vaults_get"))
            else:
                flash("Vault created sucessfully!", "success")
                session.modified = True
                return redirect(url_for("vaults.vaults_get"))
        
@vaults.route("/update_vault/<vault_name>", methods=["POST"])
def update_vault_post(vault_name):
    if not session.get("name"):
        return redirect(url_for("index"))
    else:
        vault_backup = copy.deepcopy(session["vault"][vault_name])
        
        form = request.form.to_dict(flat=False)
        try:
            vault_item_keys = form["Name"]
            vault_item_values = form["Password"]
        except KeyError:
            # Removes all items
            vault_item_keys = []
            vault_item_values = []
        
        unvalid_passwords = False
        for i in list(session["vault"][vault_name].keys()):
            if not i in vault_item_keys:
                del session["vault"][vault_name][i]
        for index, key in enumerate(vault_item_keys):
            password = vault_item_values[index]
            is_valid_password, reason = psw_validation.validate(password)
            if is_valid_password:
                session["vault"][vault_name][key] = vault_item_values[index]
            else:
                unvalid_passwords = True
                flash(f"Could not save '{key}': {reason}", "error")
        session.modified = True
        encrypted_vault = crypto.encrypt(session["key"], json.dumps(session["vault"]))
        success, reason = mongo.update_vault(session["name"], encrypted_vault)
        if not success:
            session["vault"][vault_name] = vault_backup
            flash(reason, "error")
            return redirect(f"/vaults/{vault_name}")
        else:
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
        vault_backup = copy.deepcopy(session["vault"][vault_name])
        del session["vault"][vault_name]
        session.modified = True
        encrypted_vault = crypto.encrypt(session["key"], json.dumps(session["vault"]))
        success, reason = mongo.update_vault(session["name"], encrypted_vault)
        if not success:
            session["vault"][vault_name] = vault_backup
            flash(reason, "error")
            return redirect(url_for("vaults.vaults_get"))
        else:
            flash("Vault removed succesfully!", "success")
            return redirect(url_for("vaults.vaults_get"))