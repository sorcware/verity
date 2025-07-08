import logging
from typing import List

from api.src.category import Category
from api.src.data_handler import Database
from api.src.account import (
    Account,
    currentAccount,
    cashAccount,
    savingAccount,
    creditAccount,
    untrackedAccount,
)

logger = logging.getLogger(__name__)


class User:
    "Main user class, for anything related to the user"

    def __init__(self, database: Database, user_name: str = "", id: int = 0):
        self.database: Database = database
        self.name: str = user_name
        self.id: int = id
        self.categories: List[Category] = []
        self.internal_category_id = 0
        self.accounts: list[Account] = []
        logger.info(f"{self.name} initialised.")

    def __str__(self):
        return f"User is {self.name}"

    def add(self) -> int:
        logger.info(f"adding user {self.name}")
        sql = "INSERT INTO USER(name) VALUES (?)"
        params = (self.name,)
        success, self.id = self.database.execute(sql, params, return_id=True)
        if not success:
            logger.error(f"Failed to insert user {self.name} Please check the logs")
            return 0
        category_sql = """INSERT INTO category (user_id, name, budget_value, parent_id)
            VALUES (?, ?, ?, ?)"""
        category_params = (self.id, "internal_master_category", 0, None)
        category_success, default_category_id = self.database.execute(
            category_sql, category_params, return_id=True, seed=True
        )
        if not category_success:
            logger.error(f"Failed to add default category for {self.name} Please check the logs")
        # if category fails to add,
        # we probably need to delete the user, so we dont lock the username
        logger.info(f"master_category id = {default_category_id}")
        self.internal_category_id = default_category_id
        return self.id

    def exists(self) -> bool:
        logger.info(f"Checking to see if {self.name} already exists!")
        sql = "SELECT 1 FROM user where name = ?"
        params = (self.name,)
        user_in_db = self.database.read(sql, params)
        logger.info(user_in_db)
        if user_in_db:
            logger.warning(f"{self.name} already exists in the database")
            return True
        return False

    def get_categories(self):
        "Gets all top level categories for the user"
        logger.info(f"Getting Categories for {self.name}")
        sql = """
        SELECT id, name, budget_value
        FROM category
        WHERE user_id = ?
        AND parent_id = ?
        """
        if self.internal_category_id == 0:
            self.get_internal_master_category()
        params = (self.id, self.internal_category_id)
        categories = self.database.read(sql, params)
        logger.info(f"categories: {categories}")
        for category in categories:
            cat = Category(self.database, self.id, category[1], category[2], category[0])
            self.categories.append(cat)
        return self.categories

    def get(self):
        logger.info("Getting details for User")
        sql = """
        SELECT name
        FROM user
        WHERE id = ?
        """
        params = (self.id,)
        name = self.database.read(sql, params)
        logger.info(name)
        name = name[0][0]
        logger.info(name)
        self.name = name

    def get_internal_master_category(self):
        sql = """
        SELECT id FROM category WHERE name = ? and user_id = ?
        """
        params = ("internal_master_category", self.id)
        master_id = self.database.read(sql, params)
        try:
            master_id = master_id[0][0]
        except Exception:
            master_id = 0
        self.internal_category_id = master_id
