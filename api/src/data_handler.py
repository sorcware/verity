import logging
import sqlite3

logger = logging.getLogger(__name__)


class Database:
    """basic Database class to start some development
    Will need a proper refactor once basic functions are in and working
    This is POC
    """

    def __init__(self, config) -> None:
        self.verity_config = config
        self.schema = self.verity_config.DATABASE_SCHEMA
        self.database = self.verity_config.DATABASE

    def execute(
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
                logger.debug(f"Returning tuple (success), (new id) ({is_success},{new_id})")
                return (is_success, new_id)
            else:
                logger.debug(f"Returning success value {is_success}")
                return is_success

    def read(self, sql_statement: str, params: tuple = ()) -> list:
        "reads the database query and returns the results"
        logger.info(f"received request to read {sql_statement} with params {params}")
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
        table_name = table["table_name"]
        sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
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
            
            # Check for missing columns in existing table
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            for column in table["table_columns"]:
                col_name = column["column_name"]
                if col_name not in existing_columns:
                    logger.info(f"Adding missing column {col_name} to table {table_name}")
                    # Build column definition for ALTER TABLE
                    # Note: SQLite ALTER TABLE ADD COLUMN has some restrictions (e.g. can't be PRIMARY KEY)
                    # But for simple columns like 'balance' it works.
                    # We need to reconstruct the type and constraints.
                    col_def = self._build_column(column)
                    # _build_column returns "name type constraints", we just need "ADD COLUMN name type constraints"
                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_def}"
                    try:
                        cursor.execute(alter_sql)
                        logger.info(f"Added column {col_name}")
                    except sqlite3.OperationalError as e:
                        logger.error(f"Failed to add column {col_name}: {e}")

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

    def seed_static_data(self):
        """Populates static data tables like account_type"""
        account_types = [
            (1, "Current"),
            (2, "Cash"),
            (3, "Saving"),
            (4, "Credit"),
            (5, "Untracked"),
        ]
        for type_id, name in account_types:
            # Check if exists first to avoid unique constraint errors if re-running
            check_sql = "SELECT 1 FROM account_type WHERE id = ?"
            if not self.read(check_sql, (type_id,)):
                logger.info(f"Seeding account_type {name}")
                self.execute("INSERT INTO account_type (id, name) VALUES (?, ?)", (type_id, name))

    def build_database(self):
        for table in self.schema["tables"]:
            logger.info(f"Checking {table['table_name']}")
            # Add true/false handling here to gracefully handle errors
            self._add_table_to_db(table)
        self.seed_static_data()

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

    def get_users(self) -> list:
        """Returns all users in the database."""
        get_user_sql = "SELECT id, name FROM user"
        return self.read(get_user_sql)
