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

    def execute_sql(self, sql_statement: str, return_id: bool = False) -> (bool, int):
        "send the query here, returns true if successful, false if fail"
        logging.debug(f"received request to execute {sql_statement}")
        new_id: int = 0
        is_success: bool = False
        try:
            connection = sqlite3.connect(
                database=self.database,
                timeout=10,  # seconds i hope
            )
            logging.debug("opened connection to database")
            cursor = connection.cursor()
            cursor.execute(sql_statement, {})
            connection.commit()
            if return_id:
                new_id = cursor.lastrowid
            is_success = True
        except Exception as e:  # TODO: better Exception handling
            logging.error(e)
            is_success = False
        finally:
            connection.close()
            if return_id:
                return (is_success, new_id)
            else:
                return is_success

    def read_database(self, sql_statement: str):
        "reads the database query and returns the results"
        logging.debug(f"received request to read {sql_statement}")
        results = 0
        try:
            connection = sqlite3.connect(self.database)
            logging.debug("opened connection to database")
            cursor = connection.cursor()
            results = cursor.execute(sql_statement, {})
            results = results.fetchall()
            logging.debug(f"query returned: {results}")
        except Exception as e:
            logging.error(f"Read error occured: {e}")
        finally:
            connection.close()
            return results

    @staticmethod
    def _build_column(column: dict) -> str:
        logging.debug(
            f"building column {column}"
        )
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
                logger.debug(
                    f"Column Name: {row[1]}, Data Type: {row[2]}, Not Null: {row[3]}"
                )

        except Exception as e:
            logger.error(f"An error occurred: {e}")

        finally:
            try:
                connection.close()
            except Exception as e:
                logger.error(e)

    def add_user_name(self, user_name: str) -> int:
        "takes user name string, returns user id"
        logger.debug(
            f"attempting to insert values into user table {user_name}"
        )
        try:
            connection = sqlite3.connect(self.database)
            logger.debug("connection to db open")
            cursor = connection.cursor()
            logger.debug("cursor activated")
            cursor.execute(
                """INSERT INTO user (
            name
            )
            VALUES (?)
            """,
                (user_name,),
            )
            logger.debug("cursor executed")
            connection.commit()
            user_id = cursor.lastrowid
            logger.debug(f"insert attempt seems successful, user id is {user_id}")

            if user_id is None:
                user_id = 0
        except Exception as e:
            logger.error(f"Failed to insert user name, error: {e}")
            user_id = 0
        finally:
            try:
                connection.close()
                logger.debug("connection to db closed")
                return user_id
            except Exception as e:
                logger.error(f"failed to close connection message: {e}")
                return 0

    def get_users(self) -> list:
        get_user_sql = "SELECT name FROM user"
        users = self.read_database(get_user_sql)
        return users
