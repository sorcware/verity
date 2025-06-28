import logging
import sqlite3

logger = logging.getLogger(__name__)


class database:
    """basic Database class to start some development
    Will need a proper refactor once basic functions are in and working
    This is POC
    """

    def __init__(self, config) -> None:
        self.verity_config = config
        self.schema = self.verity_config.DATABASE_SCHEMA
        self.database = self.verity_config.DATABASE
        self.default_data = self.verity_config.DEFAULT_DATA

    def execute_sql(
        self, sql_statement: str, params: tuple = (), return_id: bool = False, seed: bool = False
    ) -> (bool, int):
        "send the query here, returns true if successful, false if fail"
        logger.debug(f"received request to execute {sql_statement} with params {params}")
        new_id: int = 0
        is_success: bool = False
        try:
            connection = sqlite3.connect(
                database=self.database,
                timeout=10,  # seconds i hope
            )
            logger.info("opened connection to database")
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            if seed:
                cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute(sql_statement, params)
            connection.commit()
            logger.debug(f"executed {sql_statement} with params: {params}")
            logger.info("executed sql command")
            if return_id:
                new_id = cursor.lastrowid
                logger.debug(f"New id created {new_id}")
            is_success = True
        except Exception as e:  # TODO: better Exception handling
            logger.error(e)
            is_success = False
        finally:
            cursor.execute("PRAGMA foreign_keys = ON;")
            connection.close()
            logger.info("closed connection to database")
            if return_id:
                return (is_success, new_id)
            else:
                return is_success

    def read_database(self, sql_statement: str, params: tuple = ()) -> list:
        "reads the database query and returns the results"
        logger.debug(f"received request to read {sql_statement} with params {params}")
        results = []
        try:
            connection = sqlite3.connect(self.database)
            cursor = connection.cursor()
            results = cursor.execute(sql_statement, params)
            results = results.fetchall()
            logger.debug(f"query returned: {results}")
        except Exception as e:
            logger.error(f"Read error occurred: {e}")
        finally:
            connection.close()
            return results

    @staticmethod
    def _build_column(column: dict) -> str:
        logging.debug(f"building column {column}")
        name = column["column_name"]
        is_pk = column["is_pk"]
        is_fk = column.get("is_fk")
        datatype = column["datatype"]
        nullable = column["nullable"]
        column_string = f"{name} {datatype}"
        if is_pk:
            column_string += " PRIMARY KEY AUTOINCREMENT"
        if is_fk:
            column_string += f" REFERENCES {column['is_fk']} "
        if not nullable:
            column_string += " NOT NULL"
        return column_string

    def _add_table_to_db(self, table: dict) -> bool:
        "Creates the table in the verity database, based on the schema yaml"
        sql = f"""CREATE TABLE IF NOT EXISTS {table["table_name"]} (
        """
        columns = []
        for column in table["table_columns"]:
            columns.append(self._build_column(column))
        sql += ",\n".join(columns)
        sql += "\n);"
        success_status = False
        try:
            connection = sqlite3.connect(self.database)
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()
            success_status = True
        except sqlite3.ProgrammingError as pe:
            logger.error(pe)
        except sqlite3.OperationalError as oe:
            logger.error(oe)
        except sqlite3.InterfaceError as ie:
            logger.error(ie)
        finally:
            try:
                connection.close()
            except Exception as e:
                logger.error(e)
            return success_status

    def build_database(self):
        for table in self.schema["tables"]:
            logger.info(f"Checking {table['table_name']}")
            # Add true/false handling here to gracefully handle errors
            self._add_table_to_db(table)

    def print_table_schema(self, table_name):
        """
        Connects to the sqlite3 database,
        retrieves the schema of a specified table,
        and prints it to the console.

        Args:
            table_name (str): The name of the table to inspect.
        """
        try:
            connection = sqlite3.connect(self.database)
            cursor = connection.cursor()

            # Use PRAGMA table_info to get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")

            # Print the schema
            logger.debug(f"Schema for table: {table_name}")
            for row in cursor.fetchall():
                logger.debug(f"Column Name: {row[1]}, Data Type: {row[2]}, Not Null: {row[3]}")

        except Exception as e:
            logger.error(f"An error occurred: {e}")

        finally:
            try:
                connection.close()
            except Exception as e:
                logger.error(e)

    def add_user_name(self, user_name: str) -> int:
        "takes user name string, returns user id"
        logger.debug(f"attempting to insert values into user table {user_name}")
        sql_statement = """
        INSERT INTO user (name)
        VALUES (?)
        """
        params = (user_name,)
        success, user_id = self.execute_sql(sql_statement, params, True)
        if not success:
            logger.error("Failed to execute sql, check the logs")
        self.add_category(user_id, "internal_master_category", seed=True)
        return user_id

    def get_users(self) -> list:
        """Returns all users in the database."""
        get_user_sql = "SELECT id, name FROM user"
        return self.read_database(get_user_sql)

    def add_category(
        self, user_id: int, category_name: str, budget_value: int = 0, parent_id=None, seed=False
    ) -> int:
        """Inserts a new category. Returns the category id."""
        logger.debug(f"attempting to insert category '{category_name}' for user {user_id}")
        sql_statement = """
        INSERT INTO category (user_id, name, budget_value, parent_id)
        VALUES (?, ?, ?, ?)"""
        if not seed:
            if not parent_id:
                parent_id = self.read_database(
                    "SELECT id FROM category WHERE user_id = ? AND name = ?",
                    (user_id, "internal_master_category"),
                )
                try:
                    parent_id = parent_id[0][0]
                except IndexError:
                    parent_id = None
        params = (user_id, category_name, budget_value, parent_id)

        success, category_id = self.execute_sql(sql_statement, params, True, seed)
        if not success:
            logger.error("Failed to execute sql, check the logs")
        return category_id

    def get_categories(self, user_id: int) -> list:
        """Returns all categories for a given user."""
        sql = (
            "SELECT id, name, budget_value, parent_id FROM category WHERE user_id = ? and name != ?"
        )
        return self.read_database(sql_statement=sql, params=(user_id, "internal_master_category"))
