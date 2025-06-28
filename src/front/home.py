import logging

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

import currency_handler
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
    # Get user info directly from session
    user_id = session.get("user_id")
    selected_user_name = session.get("user_name")

    # Debug log to see what's being passed to the template
    logger.debug(f"User ID from session: {user_id}, User Name from session: {selected_user_name}")
    logger.info(f"{selected_user_name} is logged in")

    categories = db_call.get_categories(user_id) if user_id else []
    return render_template(
        "home.html",
        users=users,
        categories=categories,
        selected_user_id=user_id,
        selected_user_name=selected_user_name,
    )


@home_bp.route("/submit_user", methods=["POST"])
def submit_user_name():
    user_name = request.form.get("userName")
    logger.debug(f"Request Received: {request.form}")
    if not user_name:
        flash("Please enter a user name.", "danger")
        return redirect(url_for("home.home_page"))

    db_call = data_handler.database(verity_config)
    # More efficient check for existing user
    exists = db_call.read_database("SELECT 1 FROM user WHERE name = ?", (user_name,))
    if exists:
        logger.warning(f"username already exists in the database: {user_name}")
        flash("A user with that name already exists.", "danger")
        return redirect(url_for("home.home_page"))
    logger.info(f"User submitted new user name: {user_name}")
    user_id = db_call.add_user_name(user_name)
    if user_id == 0:
        flash("User Name not saved, please check the logs", "danger")
        return redirect(url_for("home.home_page"))
    session["user_id"] = int(user_id)
    session["user_name"] = user_name
    flash("user name saved! Start adding categories.", "success")
    return redirect(url_for("home.home_page"))


@home_bp.route("/select_user", methods=["POST"])
def select_user():
    selected_user_id = request.form.get("selectedUserId")
    if not selected_user_id:
        flash("No user selected", "error")
        session.pop("user_id", None)
        session.pop("user_name", None)
        return redirect(url_for("home.home_page"))

    # Convert selected_user_id to int and handle invalid input
    try:
        selected_user_id = int(selected_user_id)
    except ValueError:
        logger.error(f"Invalid user ID: {selected_user_id}")
        flash("Invalid user ID", "error")
        return redirect(url_for("home.home_page"))

    # Get the user details directly from the database using the ID
    db_call = data_handler.database(verity_config)
    result = db_call.read_database("SELECT name FROM user WHERE id = ?", (selected_user_id,))

    if result and result[0]:
        # Store both ID and name in the session
        session["user_id"] = selected_user_id
        session["user_name"] = result[0][0]
        flash("User selected!", "success")
    else:
        session.pop("user_id", None)
        session.pop("user_name", None)
        flash("User not found!", "danger")

    return redirect(url_for("home.home_page"))


@home_bp.route("/submit_category", methods=["POST"])
def submit_category():
    user_id = session.get("user_id")
    if not user_id:
        logger.warning("No user selected and trying to add a category... how?")
        flash("No user selected!", "danger")
        return redirect(url_for("home.home_page"))

    # Get and validate category name (required)
    category_name = request.form.get("categoryName")

    # Convert budget_value to our universal currency
    budget_value: int = 0
    budget_value_input = request.form.get("budgetValue", "0")
    logger.debug(f"budget value input: {budget_value_input}")
    if not budget_value_input:
        logger.info("no budget value assigned to category")
    else:
        logger.info(f"Category:{category_name}, Assigned amount: {budget_value_input}")
        # User might either add a whole currency or a decimal of. we need to handle both
        if float(budget_value_input) < 0:
            logger.info("user is stupid and tried to assign a negative amount to the category")
            flash("Negative amounts don`t really make sense here, removed budget amount", "danger")
            budget_value_input = 0
        budget_value = currency_handler.convert_to_universal_currency(budget_value_input)
    # Convert parent_id to int if provided
    parent_id = request.form.get("parentId", "0").strip()

    db_call = data_handler.database(verity_config)
    if parent_id == 0:
        category_id = db_call.add_category(user_id, category_name, budget_value)
    else:
        category_id = db_call.add_category(user_id, category_name, budget_value, parent_id)
    if category_id == 0:
        flash("Category not saved, please check the logs", "danger")
    else:
        flash("Category saved!", "success")
    return redirect(url_for("home.home_page"))
