# Accounts



The Attributes of the accounts class are:

- database (Database Object)
    * passed in so we can test with a theoretical database

- name (String)
    * The name of the account as stored in the database

- id (int)
    * the id of the account as stored in the database

The Methods of the account class are:

- add
    * Adds the account to the database

- get_name
    * Gets the name of the account, sets it in the name attribute

- get_id
    * gets the id od the account, sets it in the id attribute 

- get
    * gets all sored information about the account 
    * _Probably_ returns the results, so we can build an object with the data.

The Attribute class is a parent class to the following children:
The use case of these will allow for more fexible handling of specific tasks that each account type
will be able to do.

- CurrentAccount
- cashAccount
- savingAccount
- creditAccount
- untrackedAccount
