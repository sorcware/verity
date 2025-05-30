import logging

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

import data_handler
from config import VerityConfig

logger = logging.getLogger(__name__)

home_bp = Blueprint("home", __name__, template_folder="templates")
verity_config = VerityConfig()


@home_bp.route("/")
def home_page():
    logger.info("home page hit")
    db_call = data_handler.database(verity_config)
    users = db_call.get_users()
    return render_template("home.html", users=users)


@home_bp.route("/submit", methods=["POST"])
def submit_user_name():
    user_name = request.form.get("userName")
    logger.debug(f"Request Received: {request.form}")
    if user_name:
        logger.info(f"User submitted new user name: {user_name}")
        session["user_name"] = user_name
        db_call = data_handler.database(verity_config)
        user_id = db_call.add_user_name(user_name)
        if user_id == 0:
            # db entry failed, throw error message
            flash("User Name not saved, please check the logs", "error")
            return redirect(url_for("home.home_page"))
        session["user_id"] = user_id
        flash("user name saved!", "success")
        return redirect(url_for("home.home_page"))
    else:
        flash("Please enter a user name.", "error")
        return redirect(url_for("home.home_page"))
