"Account Module"

import logging

from api.src.user import User  # probably the other way round
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


class cashAccount(Account):
    "Cash Account for tracking your real money"


class savingAccount(Account):
    "Saving Account for tracking your savings"


class creditAccount(Account):
    "Credit Acount, for tracking your debts like credit cards"


class untrackedAccount(Account):
    "for money you still want to see, but dont use as part of your budget."
