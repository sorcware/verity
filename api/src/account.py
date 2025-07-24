"Account Module"

import logging

from api.src.data_handler import Database

logger = logging.getLogger(__name__)


class Account:
    "Main account class for any 'real' storage of currency"

    def __init__(self, database: Database, name: str = "", id: int = 0, user_id: int = 0):
        self.database = database
        self.name = name
        self.id = id
        self.user_id = user_id
        self.type = ""
        self.balance = 0
        logger.info(f"Account {self.name} | {self.id} initialised")

    def __repr__(self):
        return f"""Account:(
        Name: {self.name}
        Id: {self.id}
        Type: {self.type}
        Balance: {self.balance}
        )
        """

    def __str__(self):
        return f"Account: {self.name} of type: {self.type}"

    def add(self):
        "add account to database"
        logger.info(f"Adding {self.name} to {self.user_id}")
        if self.user_id == 0:
            logger.error("Account not attached to a user, cannot continue")
            return 0
        if not self.type_id:
            logger.error("Cannot add a non-typed account, please use Children of Account")
            return 0
        sql_statement = """
        INSERT INTO account (user_id, type_id, name, balance)
        VALUES (?, ?, ?, ?)
        """
        params = (self.user_id, self.type_id, self.name, self.balance)
        success, self.id = self.database.execute(sql_statement, params, return_id=True)
        if not success:
            logger.error(f"Failed to add Account {self.name}, Check the logs")
        return self.id

    def get_name(self):
        "get name with id"
        pass

    def get_id(self):
        "get id with name"
        pass

    def get(self):
        "get account details from database"
        pass


class currentAccount(Account):
    "Current Bank Account for every day banking"

    def __init__(self, database, name, id):
        self.type = "Current"
        self.type_id = 1
        super(currentAccount, self).__init__(database, name, id)


class cashAccount(Account):
    "Cash Account for tracking your real money"

    def __init__(self, database, name, id):
        self.type = "Cash"
        self.type_id = 2
        super(currentAccount, self).__init__(database, name, id)


class savingAccount(Account):
    "Saving Account for tracking your savings"

    def __init__(self, database, name, id):
        self.type = "Saving"
        self.type_id = 2
        super(currentAccount, self).__init__(database, name, id)


class creditAccount(Account):
    "Credit Acount, for tracking your debts like credit cards"

    def __init__(self, database, name, id):
        self.type = "Credit"
        self.type_id = 3
        super(currentAccount, self).__init__(database, name, id)


class untrackedAccount(Account):
    "for money you still want to see, but dont use as part of your budget."

    def __init__(self, database, name, id):
        self.type = "Untracked"
        self.type_id = 4
        super(currentAccount, self).__init__(database, name, id)
