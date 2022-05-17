from flask import Blueprint, render_template, url_for, flash
from .forms import RegisterForm
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(first_name=form.first_name.data,
                        email_address=form.email_address.data,
                        password=form.password1.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f"Account created successfully!", category='success')

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Error Creating Account: {err_msg}', category='danger')

    return render_template("register.html", form=form)
