from flask import Blueprint, render_template, request, redirect, flash, current_app
from models.user_model import db, User
from models.file_model import File
from utils.auth_decorators import login_required, admin_required
from utils.hash_utils import hash_password
from utils.crypto_utils import generate_rsa_keys
import os
import json

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@login_required
@admin_required
def admin_home():
    return render_template("admin/admin_home.html")


# list users
@admin_bp.route("/admin/user/list")
@login_required
@admin_required
def user_list():

    users = User.query.all()

    return render_template("admin/user_list.html", users=users)


# view user
@admin_bp.route("/admin/user/<int:user_id>")
@login_required
@admin_required
def view_user(user_id):

    user = User.query.get(user_id)

    return render_template("admin/user_view.html", user=user)


# delete user
@admin_bp.route("/admin/user/delete/<int:user_id>")
@login_required
@admin_required
def delete_user(user_id):

    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect("/admin/user/list")


# edit user
@admin_bp.route("/admin/user/edit/<int:user_id>", methods=["GET","POST"])
@login_required
@admin_required
def edit_user(user_id):

    user = User.query.get(user_id)

    if request.method == "POST":

        user.name = request.form["name"]
        user.email = request.form["email"]

        db.session.commit()

        return redirect("/admin/user/list")

    return render_template("admin/user_edit.html", user=user)


# add user
@admin_bp.route("/admin/user/add", methods=["GET","POST"])
@login_required
@admin_required
def add_user():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        name = request.form["name"]
        email = request.form["email"]

        hashed = hash_password(username, password)
        pub_key, priv_key = generate_rsa_keys()

        user = User(
            username=username,
            password=hashed,
            role="user",
            name=name,
            email=email,
            rsa_public_key=pub_key,
            rsa_private_key=priv_key
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/admin/user/list")

    return render_template("admin/user_add.html")


@admin_bp.route("/admin/user/reset_password/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    
    # Reset to default password "123"
    new_hashed = hash_password(user.username, "123")
    user.password = new_hashed
    
    db.session.commit()
    flash(f"Mật khẩu của {user.username} đã được reset về '123'.", "success")
    return redirect("/admin/user/list")


# FILE MANAGEMENT FOR ADMIN

@admin_bp.route("/admin/file/list")
@login_required
@admin_required
def file_list():
    files = File.query.all()
    
    # Pre-process files for template
    processed_files = []
    for f in files:
        shared_ids = []
        if f.shared_with not in ["-1", "0"]:
            try:
                shared_ids = json.loads(f.shared_with)
            except:
                shared_ids = []
        f.shared_ids = shared_ids
        processed_files.append(f)
        
    all_users = User.query.all()
    
    return render_template("admin/file_list.html", files=processed_files, all_users=all_users)


@admin_bp.route("/admin/file/delete/<int:file_id>", methods=["POST"])
@login_required
@admin_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Delete from folder
    file_path = os.path.join(current_app.root_path, 'uploads', file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete from DB
    db.session.delete(file)
    db.session.commit()
    
    flash("File deleted successfully.")
    return redirect("/admin/file/list")


@admin_bp.route("/admin/file/edit/<int:file_id>", methods=["POST"])
@login_required
@admin_required
def edit_file(file_id):
    file = File.query.get_or_404(file_id)
    
    status = int(request.form.get("status", 0))
    sharing_type = request.form.get("sharing_type", "private")
    
    if status == 0:
        file.status = 0
        file.shared_with = "-1"
    else:
        file.status = 1
        if sharing_type == "all":
            file.shared_with = "0"
        elif sharing_type == "specific":
            shared_ids = request.form.getlist("shared_users")
            file.shared_with = json.dumps([int(uid) for uid in shared_ids])
        else:
            file.shared_with = "0"
            
    db.session.commit()
    flash("File updated successfully.")
    return redirect("/admin/file/list")