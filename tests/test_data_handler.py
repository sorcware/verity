import os
import tempfile

import pytest

from api.src.config import VerityConfig
from api.src.data_handler import Database


@pytest.fixture
def test_db_call():
    """Create a test database instance with a unique test database file"""
    config = VerityConfig()
    # Use a test-specific database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        test_db_file = temp_db.name

    # Create a config with the test DB
    config.DATABASE = test_db_file
    db_call = Database(config)
    db_call.build_database()
    yield db_call
    # Cleanup after tests
    if os.path.exists(test_db_file):
        os.remove(test_db_file)


def test_execute_success(test_db_call):
    """Test executing valid SQL statements"""
    sql_statement = """INSERT INTO user (
    name
    )
    VALUES ('a_user_name')
    """
    result = test_db_call.execute(sql_statement)
    assert result is True


def test_execute_error(test_db_call):
    """Test executing invalid SQL statements"""
    sql_statement = "SELECT * FROM non_existent_table"
    result = test_db_call.execute(sql_statement)
    assert result is False


def test_execute_with_return_id(test_db_call):
    """Test executing SQL with return_id flag"""
    sql_statement = """INSERT INTO user (
    name
    )
    VALUES ('return_id_test')
    """
    result, new_id = test_db_call.execute(sql_statement, return_id=True)
    assert result is True
    assert new_id > 0


def test_read(test_db_call):
    """Test reading database data"""
    # First insert a user
    insert_sql = """INSERT INTO user (
    name
    )
    VALUES ('read_test_user')
    """
    _ = test_db_call.execute(insert_sql)
    # Then read it back
    sql_statement = "SELECT id, name FROM user WHERE name = 'read_test_user'"
    results = test_db_call.read(sql_statement)
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0][1] == "read_test_user"


def test_read_with_params(test_db_call):
    """Test reading database with parameterized query"""
    # First insert a user
    insert_sql = """INSERT INTO user (
    name
    )
    VALUES ('param_test_user')
    """
    _ = test_db_call.execute(insert_sql)  # Then read it back with params
    sql_statement = "SELECT id, name FROM user WHERE name = ?"
    params = ("param_test_user",)
    results = test_db_call.read(sql_statement, params)
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0][1] == "param_test_user"


def test_build_database(test_db_call):
    """Test that the database builds correctly with all required tables"""
    # Check if all tables have been created
    config = VerityConfig()
    for table in config.DATABASE_SCHEMA["tables"]:
        table_name = table["table_name"]
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        results = test_db_call.read(sql)
        assert len(results) == 1, f"Table '{table}' should exist"


# TODO: Put the below tests in their respective test files (user and category)

# def test_add_user_name(test_db_call):
#     """Test adding a new user name"""
#     user_name = "Test user"
#     user_id = test_db_call.add_user_name(user_name)
#     assert user_id > 0
#
#     # Check if the user name was actually added
#     sql = "SELECT id, name FROM user WHERE name = ?"
#     results = test_db_call.read(sql, (user_name,))
#     assert len(results) == 1
#     assert results[0][1] == user_name
#
#
# def test_add_duplicate_user_name(test_db_call):
#     """Test adding a duplicate user name (should succeed at DB level without constraints)"""
#     user_name = "Duplicate User"
#     # Add first user
#     user_id1 = test_db_call.add_user_name(user_name)
#     assert user_id1 > 0
#
#     # Add second user with same name
#     user_id2 = test_db_call.add_user_name(user_name)
#     assert user_id2 > 0
#     assert user_id2 != user_id1  # They should have different IDs
#
#
# def test_get_users(test_db_call):
#     """Test getting all users"""
#     # Add some test users first
#     test_db_call.add_user_name("User One")
#     test_db_call.add_user_name("User Two")
#
#     # Get users
#     users = test_db_call.get_users()
#     assert isinstance(users, list)
#     assert len(users) >= 2
#
#     # Check that users are returned as (id, name) tuples
#     for user in users:
#         assert len(user) == 2
#         assert isinstance(user[0], int)  # ID
#         assert isinstance(user[1], str)  # Name
#
#
# def test_add_category_success(test_db_call):
#     # Add a user first, since category requires a user_id
#     user_id = test_db_call.add_user_name("CategoryTestUser")
#     assert user_id != 0
#     # Add a category with all fields
#     category_id = test_db_call.add_category(user_id, "Groceries", 200.0, None)
#     assert category_id != 0
#     # Add a category with only required fields
#     category_id2 = test_db_call.add_category(user_id, "Utilities")
#     assert category_id2 != 0
#
#
# def test_add_category_null_budget_and_parent(test_db_call):
#     user_id = test_db_call.add_user_name("NullBudgetParentUser")
#     assert user_id != 0
#     # Add a category with None for budget_value and parent_id
#     category_id = test_db_call.add_category(user_id, "NoBudgetOrParent", None, None)
#     assert category_id != 0
#
#
# def test_add_category_and_get_categories(test_db_call):
#     # Add a user
#     user_name = "CategoryTestUser"
#     user_id = test_db_call.add_user_name(user_name)
#     assert user_id != 0
#     # Add a category for this user
#     category_name = "Groceries"
#     budget_value = 100.0
#     parent_id = None
#     category_id = test_db_call.add_category(user_id, category_name, budget_value, parent_id)
#     assert category_id != 0
#     # Add a subcategory
#     subcategory_name = "Supermarket"
#     subcategory_id = test_db_call.add_category(user_id, subcategory_name, 50.0, category_id)
#     assert subcategory_id != 0
#     # Retrieve categories for this user
#     categories = test_db_call.get_categories(user_id)
#     assert isinstance(categories, list)
#     names = [cat[1] for cat in categories]
#     assert category_name in names
#     assert subcategory_name in names
#
#
# def test_add_category_invalid_user(test_db_call):
#     # Try to add a category with a non-existent user_id
#     # (should still succeed in SQLite unless foreign keys are enforced)
#     category_id = test_db_call.add_category(99999, "InvalidUserCategory")
#     assert category_id == 0
#     assert isinstance(category_id, int)
