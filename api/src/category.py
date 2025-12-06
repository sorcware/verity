import logging
from typing import Optional

from api.src.data_handler import Database

# from api.src.user import User

logger = logging.getLogger(__name__)


class Category:
    "Main category class, for any theoretical storage of currency"

    def __init__(
        self,
        database: Database,
        user_id: int,
        category_name: str = "",
        budget_value: int = 0,
        id: int = 0,
        parent: Optional["Category"] = None,
    ):
        self.database: Database = database
        self.name: str = category_name
        self.budget_value: int = budget_value
        self.id: int = id
        self.children: list[Category] = []
        self.parent: Category = parent
        self.user_id = user_id
        if not self.name:
            self.get_name()
        logger.info(f"{self.name} / {self.id} initialised")

    def __repr__(self):
        return f"""Category:(
        Name: {self.name}
        Id: {self.id}
        Budget Value: {self.budget_value}
        Number of Childen: {len(self.children)}
        Parent:{self.parent.name if self.parent else "Top Level Category"}
        )"""

    def __str__(self):
        return f"Category: {self.name}"

    def add(self):
        logger.info(f"Adding {self.name} to user id {self.user_id}")
        sql_statement = """
        INSERT INTO category (user_id, name, budget_value, parent_id)
        VALUES (?, ?, ?, ?)
        """
        if not self.parent:
            logger.debug("No parent linked to category, linking now.")
            self.get_default_category()
        params = (self.user_id, self.name, self.budget_value, int(self.parent.id))
        success, self.id = self.database.execute(sql_statement, params, return_id=True)
        if not success:
            logger.error(f"Failed to add Category {self.name} Check the logs")
        return self.id

    def get_default_category(self):
        logger.info("Getting Default Category")
        self.parent = Category(self.database, self.user_id, "internal_master_category")
        logger.info(f"master category = {self.parent}")
        self.parent.get_id()
        logger.info(f"parent id = {self.parent.id}")

    def get_id(self):
        logger.info(f"Getting Category id for {self.name}")
        category_id_sql = "SELECT id FROM category WHERE user_id = ? AND name = ?"
        category_id_params = (self.user_id, self.name)
        category_id = self.database.read(category_id_sql, category_id_params)
        logger.info(f"Category id is {category_id}")
        try:
            self.id = category_id[0][0]
        except IndexError:
            self.id = 0

    def get_name(self):
        logger.info(f"Getting Name for Category {self.id}")
        cat_name_sql = "SELECT name FROM category WHERE user_id = ? and id = ?"
        cat_name_params = (self.user_id, self.id)
        cat_name = self.database.read(cat_name_sql, cat_name_params)
        logger.debug(f"Category name returned {cat_name}")
        try:
            self.name = cat_name[0][0]
        except IndexError:
            self.name = "Unknown"

    def get_children(self):
        logger.info(f"Getting Child Categories for {self.name}")
        sql = """
        SELECT id, name, budget_value
        FROM category
        WHERE user_id = ?
        AND parent_id = ?
        """
        params = (self.user_id, self.id)
        child_categories = self.database.read(sql, params)
        for child in child_categories:
            category = Category(self.database, self.user_id, child[1], child[2], child[0])
            self.children.append(category)

    def get(self):
        logger.info(f"Getting details for {self.name} from database")
        sql = """SELECT user_id, name, budget_value, id, parent_id
        FROM category
        WHERE id = ?
            AND user_id = ?
        """
        params = (self.id, self.user_id)
        return self.database.read(sql, params)
