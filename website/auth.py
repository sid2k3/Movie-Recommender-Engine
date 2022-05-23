from flask import Blueprint, render_template, url_for, flash, redirect, current_app as app
from .forms import RegisterForm, LoginForm
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    hall_of_fame = app.hall_of_fame()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()

        if user:  # user exists in database
            tried_password = form.password.data

            if check_password_hash(user.password, tried_password):
                # password is correct
                login_user(user)
                flash(f'Successfully logged in as {user.first_name}', category='success')
                return redirect(url_for('views.home'))
            else:
                flash(f"Incorrect Password", category='danger')
        else:
            flash("Account does not exist", category="danger")

    return render_template("login.html", form=form, hall_of_fame=hall_of_fame)


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(first_name=form.first_name.data,
                        email_address=form.email_address.data,
                        password=generate_password_hash(
                            form.password1.data, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash(f"Account created successfully! You are now logged in as {new_user.first_name}", category='success')
        return redirect(url_for('views.home'))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Error Creating Account: {err_msg}', category='danger')

    return render_template("register.html", form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", category='info')
    return redirect(url_for("auth.login"))
