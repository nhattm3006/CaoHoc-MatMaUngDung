from flask import Blueprint, render_template, request, current_app, redirect, flash, jsonify, send_from_directory, g
from models.user_model import db, User
from models.file_model import File
from models.notification_model import Notification
from utils.auth_decorators import login_required
from utils.upload_file import save_file
from utils.crypto_utils import sign_data
import os
import json

file_bp = Blueprint("file", __name__)

@file_bp.route("/myfile", methods=["GET", "POST"])
@login_required
def myfile():
    user = User.query.filter_by(username=g.user["username"]).first()
    
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file part")
            return redirect("/myfile")
        
        file = request.files['file']
        sharing_type = request.form.get("sharing_type", "private") # private, all, specific
        
        status = 0
        shared_with = "-1"
        
        if sharing_type == "all":
            status = 1
            shared_with = "0"
        elif sharing_type == "specific":
            status = 1
            shared_users = request.form.getlist("shared_users")
            shared_with = json.dumps([int(uid) for uid in shared_users])
        
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        # Digital Signature Logic
        signature = None
        if user.rsa_private_key:
            # We need to read the file content to sign it
            file.seek(0)
            data = file.read()
            file.seek(0) # Reset pointer for save_file
            signature = sign_data(user.rsa_private_key, data)

        filename, error = save_file(file, upload_folder)
        
        if error:
            flash(error)
            return redirect("/myfile")

        new_file = File(
            filename=filename,
            owner_id=user.id,
            status=status,
            shared_with=shared_with,
            signature=signature
        )
        db.session.add(new_file)
        db.session.commit()
        
        # Create Notifications
        if status == 1:
            from flask import url_for
            share_link = url_for('file.shared_files')
            msg = f"{user.username} đã chia sẻ công khai một file mới: {filename}" if shared_with == "0" else f"{user.username} đã chia sẻ một file với bạn: {filename}"
            
            if shared_with == "0":
                all_users = User.query.filter(User.id != user.id).all()
                for u in all_users:
                    db.session.add(Notification(user_id=u.id, message=msg, link=share_link))
            else:
                try:
                    target_uids = json.loads(shared_with)
                    for uid in target_uids:
                        db.session.add(Notification(user_id=uid, message=msg, link=share_link))
                except:
                    pass
            db.session.commit()
        
        return redirect("/myfile")

    # Pre-process files to decode shared_with for the template
    processed_files = []
    for f in user.files:
        shared_ids = []
        if f.shared_with not in ["-1", "0"]:
            try:
                shared_ids = json.loads(f.shared_with)
            except:
                shared_ids = []
        f.shared_ids = shared_ids # Attach temporary attribute
        processed_files.append(f)

    # Get all users (except self) for the sharing selection
    other_users = User.query.filter(User.id != user.id).all()

    return render_template("myfile.html", user_files=processed_files, all_users=other_users)

@file_bp.route("/myfile/delete/<int:file_id>", methods=["POST"])
@login_required
def delete_file(file_id):
    user = User.query.filter_by(username=g.user["username"]).first()
    file = File.query.get_or_404(file_id)
    
    if file.owner_id != user.id:
        flash("You do not have permission to delete this file.")
        return redirect("/myfile")
    
    # Delete from folder
    file_path = os.path.join(current_app.root_path, 'uploads', file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete from DB
    db.session.delete(file)
    db.session.commit()
    
    flash("File deleted successfully.")
    return redirect("/myfile")

@file_bp.route("/myfile/edit/<int:file_id>", methods=["POST"])
@login_required
def edit_file(file_id):
    user = User.query.filter_by(username=g.user["username"]).first()
    file = File.query.get_or_404(file_id)
    
    if file.owner_id != user.id:
        flash("You do not have permission to edit this file.")
        return redirect("/myfile")
    
    status = int(request.form.get("status", 0))
    sharing_type = request.form.get("sharing_type", "private") # private, all, specific
    
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
            file.shared_with = "0" # Default to all if shared but no type?
            
    db.session.commit()
    
    # Create Notifications on Edit
    if status == 1:
        from flask import url_for
        share_link = url_for('file.shared_files')
        msg = f"{user.username} đã chia sẻ công khai file: {file.filename}" if file.shared_with == "0" else f"{user.username} đã chia sẻ file với bạn: {file.filename}"
        
        if file.shared_with == "0":
            all_users = User.query.filter(User.id != user.id).all()
            for u in all_users:
                db.session.add(Notification(user_id=u.id, message=msg, link=share_link))
        elif file.shared_with not in ["-1", "0"]:
            try:
                shared_ids = json.loads(file.shared_with)
                for uid in shared_ids:
                    db.session.add(Notification(user_id=uid, message=msg, link=share_link))
            except:
                pass
        db.session.commit()

    flash("File updated successfully.")
    return redirect("/myfile")

@file_bp.route("/share")
@login_required
def shared_files():
    user = User.query.filter_by(username=g.user["username"]).first()
    
    # Get all files shared with everyone or specifically with this user
    all_shared = File.query.filter(File.status == 1, File.owner_id != user.id).all()
    
    files_for_me = []
    for f in all_shared:
        if f.shared_with == "0":
            files_for_me.append(f)
        else:
            try:
                shared_ids = json.loads(f.shared_with)
                if user.id in shared_ids:
                    files_for_me.append(f)
            except:
                continue
                
    return render_template("share.html", files=files_for_me)

@file_bp.route("/download/<int:file_id>")
@login_required
def download_file(file_id):
    user = User.query.filter_by(username=g.user["username"]).first()
    file = File.query.get_or_404(file_id)
    
    # Permission check
    can_download = False
    
    # 1. Admin can download anything
    if user.role == 'admin':
        can_download = True
    # 2. Owner can download their own files
    elif file.owner_id == user.id:
        can_download = True
    # 3. Shared files
    elif file.status == 1:
        if file.shared_with == "0": # Publicly shared
            can_download = True
        else:
            try:
                shared_ids = json.loads(file.shared_with)
                if user.id in shared_ids:
                    can_download = True
            except:
                pass

    if can_download:
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        return send_from_directory(upload_folder, file.filename, as_attachment=True)
    
    flash("You do not have permission to download this file.")
    return redirect("/")
@file_bp.route("/download_sig/<int:file_id>")
@login_required
def download_sig(file_id):
    user = User.query.filter_by(username=g.user["username"]).first()
    file = File.query.get_or_404(file_id)
    
    # Permission check (reuse logic from download_file)
    can_download = False
    if user.role == 'admin':
        can_download = True
    elif file.owner_id == user.id:
        can_download = True
    elif file.status == 1:
        if file.shared_with == "0":
            can_download = True
        else:
            try:
                shared_ids = json.loads(file.shared_with)
                if user.id in shared_ids:
                    can_download = True
            except:
                pass
                
    if not can_download:
        flash("You do not have permission to download this signature.")
        return redirect("/")
        
    if not file.signature:
        flash("File này không có chữ ký số.")
        return redirect(request.referrer or "/")

    # Return signature as a .sig file
    from flask import Response
    return Response(
        file.signature,
        mimetype="text/plain",
        headers={"Content-disposition": f"attachment; filename={file.filename}.sig"}
    )
