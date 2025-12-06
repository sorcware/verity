
import pytest
import os
import tempfile
from api.src.config import VerityConfig
from api.src.data_handler import Database
from api.src.account import Account, currentAccount, cashAccount, savingAccount, creditAccount, untrackedAccount
from api.src.user import User

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

def test_account_init(test_db_call):
    """Test basic account initialization"""
    acc = Account(test_db_call, "Test Account", 0, 1)
    assert acc.name == "Test Account"
    assert acc.user_id == 1
    assert acc.balance == 0

def test_add_account_success(test_db_call):
    """Test adding an account to the database"""
    user = User(test_db_call, "TestUser")
    user_id = user.add()
    
    acc = currentAccount(test_db_call, "My Current", 0, user_id)
    acc_id = acc.add()
    
    assert acc_id > 0
    results = test_db_call.read("SELECT name, type_id, balance FROM account WHERE id = ?", (acc_id,))
    assert results[0][0] == "My Current"
    assert results[0][1] == 1
    assert results[0][2] == 0

def test_add_account_no_user(test_db_call):
    """Test adding an account without a user_id should fail"""
    acc = currentAccount(test_db_call, "Orphan Account", 0) # user_id defaults to 0
    acc_id = acc.add()
    assert acc_id == 0

def test_account_types(test_db_call):
    """Test that all account subclasses have correct types"""
    user = User(test_db_call, "TypeTestUser")
    user_id = user.add()
    
    accounts = [
        (currentAccount(test_db_call, "C", 0, user_id), "Current", 1),
        (cashAccount(test_db_call, "Ca", 0, user_id), "Cash", 2),
        (savingAccount(test_db_call, "S", 0, user_id), "Saving", 3),
        (creditAccount(test_db_call, "Cr", 0, user_id), "Credit", 4),
        (untrackedAccount(test_db_call, "U", 0, user_id), "Untracked", 5),
    ]
    
    for acc, expected_type, expected_id in accounts:
        assert acc.type == expected_type
        assert acc.type_id == expected_id
        
        # Verify persistence
        new_id = acc.add()
        assert new_id > 0
        res = test_db_call.read("SELECT type_id FROM account WHERE id = ?", (new_id,))
        assert res[0][0] == expected_id

def test_account_balance_persistence(test_db_call):
    """Test that balance is correctly saved"""
    user = User(test_db_call, "BalanceUser")
    user_id = user.add()
    
    acc = cashAccount(test_db_call, "Wallet", 0, user_id)
    acc.balance = 150.50
    acc_id = acc.add()
    
    res = test_db_call.read("SELECT balance FROM account WHERE id = ?", (acc_id,))
    assert res[0][0] == 150.50
