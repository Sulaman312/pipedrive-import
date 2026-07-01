"""Session authentication routes."""

from flask import Blueprint, flash, redirect, request, session, url_for

from ..services import auth as auth_service
from ..views import login_page


blueprint = Blueprint("auth", __name__)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if not auth_service.is_configured():
        flash("Sign-in is not set up yet.")
        return redirect(url_for("transformations.index"))
    if request.method == "POST":
        if auth_service.credentials_match(
            request.form.get("username", ""), request.form.get("password", "")
        ):
            session.clear()
            session["authenticated"] = True
            return redirect(request.args.get("next") or url_for("transformations.index"))
        flash("Invalid username or password.")
    return login_page()


@blueprint.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
