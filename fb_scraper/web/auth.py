from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from fb_scraper.web import db, login_manager
from fb_scraper.web.forms import LoginForm
import os

bp = Blueprint("auth", __name__)

class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

@bp.before_app_first_request
def create_admin():
    admin_email = os.getenv("ADMIN_EMAIL")
    if admin_email and not User.query.filter_by(email=admin_email).first():
        admin = User(email=admin_email,
                     password=generate_password_hash(os.getenv("ADMIN_PASSWORD")))
        db.session.add(admin)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("views.index"))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
