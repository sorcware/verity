import logging
import os
import subprocess

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from api.src.account import (
    cashAccount,
    creditAccount,
    currentAccount,
    savingAccount,
    untrackedAccount,
)
from api.src.category import Category
from api.src.config import VerityConfig
from api.src.currency_handler import CurrencyBrain
from api.src.data_handler import Database
from api.src.user import User

logger = logging.getLogger(__name__)

home_bp = Blueprint("home", __name__, template_folder="templates")
# verity_config = VerityConfig()


@home_bp.route("/")
def home_page():
    logger.info("home page hit")
    db_call = Database(VerityConfig())
    users = db_call.get_users()
    # Get user info directly from session
    user_id = session.get("user_id")
    selected_user_name = session.get("user_name")
    # Debug log to see what's being passed to the template
    logger.debug(f"User ID from session: {user_id}, User Name from session: {selected_user_name}")
    logger.info(f"{selected_user_name} is logged in")
    verity_user = User(db_call, selected_user_name, user_id)
    logger.info(f"user: {verity_user}")
    if not verity_user:
        categories = []
        accounts = []
    else:
        categories = verity_user.get_categories()
        accounts = verity_user.get_accounts()
        for category in categories:
            category.get_children()
    return render_template(
        "home.html",
        users=users,
        categories=categories,
        accounts=accounts,
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

    verity_user = User(Database(VerityConfig()), user_name)
    logger.info(f"does user '{user_name}' exist?")
    if verity_user.exists():
        flash("A user with that name already exists.", "danger")
        return redirect(url_for("home.home_page"))
    logger.info(f"User submitted new user name: {user_name}")
    user_id = verity_user.add()
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
    database = Database(VerityConfig())
    verity_user = User(database, id=selected_user_id)
    verity_user.get()

    if verity_user.name and verity_user.id:
        # Store both ID and name in the session
        session["user_id"] = selected_user_id
        session["user_name"] = verity_user.name
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
        budget_value = CurrencyBrain.convert_to_universal_currency(budget_value_input)
    # Convert parent_id to int if provided
    parent_id = request.form.get("parentId", "0").strip()
    database = Database(VerityConfig())
    logger.debug(f"parent_id for new category is {parent_id}")
    if int(parent_id) == int(0):
        logger.info("user submited category with no parent, class should get default category")
        new_category = Category(
            database=database,
            user_id=user_id,
            category_name=category_name,
            budget_value=budget_value,
        )
    else:
        logger.info("user submited category with parent, class should use that id")
        parent_category = Category(database=database, user_id=user_id, id=parent_id)
        new_category = Category(
            database=database,
            user_id=user_id,
            category_name=category_name,
            budget_value=budget_value,
            parent=parent_category,
        )
    logger.info(repr(new_category))
    category_id = new_category.add()
    logger.info(repr(new_category))
    if category_id == 0:
        flash("Category not saved, please check the logs", "danger")
    else:
        flash("Category saved!", "success")
    return redirect(url_for("home.home_page"))


@home_bp.route("/submit_account", methods=["POST"])
def submit_account():
    user_id = session.get("user_id")
    if not user_id:
        flash("No user selected!", "danger")
        return redirect(url_for("home.home_page"))

    account_name = request.form.get("accountName")
    account_type = request.form.get("accountType")
    initial_balance = request.form.get("initialBalance", "0")

    try:
        balance = CurrencyBrain.convert_to_universal_currency(initial_balance)
    except Exception:
        balance = 0

    database = Database(VerityConfig())

    if account_type == "1":
        new_account = currentAccount(database, account_name, 0, user_id)
    elif account_type == "2":
        new_account = cashAccount(database, account_name, 0, user_id)
    elif account_type == "3":
        new_account = savingAccount(database, account_name, 0, user_id)
    elif account_type == "4":
        new_account = creditAccount(database, account_name, 0, user_id)
    elif account_type == "5":
        new_account = untrackedAccount(database, account_name, 0, user_id)
    else:
        flash("Invalid account type", "danger")
        return redirect(url_for("home.home_page"))

    new_account.balance = balance
    account_id = new_account.add()
    logger.info(f"Account add returned id: {account_id}")

    if account_id > 0:
        flash("Account added successfully!", "success")
    else:
        flash("Failed to add account.", "danger")

    return redirect(url_for("home.home_page"))


def stop_mdbook():
    try:
        process = subprocess.run(["pgrep", "mdbook"], capture_output=True)
        # process.kill()
        pid = process.stdout.strip()
        print(f"aiming to kill pid: {pid}")
        os.kill(int(pid), 9)
        logger.info(f"mdbook process stopped with PID: {pid}")
    except Exception as e:
        print(f"Error stopping mdbook: {e}")


@home_bp.route("/stop")
def stop_server():
    stop_mdbook()
    os.kill(os.getpid(), 9)
    return "Stopping servers... (check your logs)"
