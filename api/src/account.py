"Account Module"

import logging

from api.src.data_handler import Database

logger = logging.getLogger(__name__)


class Account:
    "Main account class for any 'real' storage of currency"

    def __init__(
        self,
        database: Database,
        name: str = "",
        id: int = 0,
    ):
        self.database = database
        self.name = name
        self.id = id
        logger.info(f"Account {self.name} | {self.id} initialised")

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def add(self):
        "add account to database"
        pass

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
        super(currentAccount, self).__init__(database, name, id)


class cashAccount(Account):
    "Cash Account for tracking your real money"

    def __init__(self, database, name, id):
        self.type = "Cash"
        super(currentAccount, self).__init__(database, name, id)


class savingAccount(Account):
    "Saving Account for tracking your savings"

    def __init__(self, database, name, id):
        self.type = "Saving"
        super(currentAccount, self).__init__(database, name, id)


class creditAccount(Account):
    "Credit Acount, for tracking your debts like credit cards"

    def __init__(self, database, name, id):
        self.type = "Credit"
        super(currentAccount, self).__init__(database, name, id)


class untrackedAccount(Account):
    "for money you still want to see, but dont use as part of your budget."

    def __init__(self, database, name, id):
        self.type = "Untracked"
        super(currentAccount, self).__init__(database, name, id)
