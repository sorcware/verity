# Users

The User as expected is the "user" of Verity, so if wanted / needed multiple users could be set up.  
The User is a logical container of all information in Verity. Meaning a user owns all other components.  


NOTE: The users are currently not password protected, so only set up & share this with users you trust.  
But also, hypothetical users could be made for various purposes, testing / demonstrating. 

Each user is completely separate from one another, so adding a category / account / transaction to
one user, will only stay on that user and not be added to another. 

The User class is initialised when logging in or creating a new user in the front end.
The User class has the following attributes:

- database (Database Object)
    * the database object is passed in so we can run tests with a theoretical database.

- name (string)
    * the name of the user as stored in the database

- id (int)
    * The id of the user as stored in the database

- categories (List of Category Objects)
    * The top level categories owned by the user.

- internal_category_id (int)
    * the internal category id for the user.

The User class has the following methods:

- add
    * adds the user to the database
    * During adding the user we add a default master category for the user
(Every transaction needs a category, so we need a master category for things like starting balance)
    * returns the user id (INT) or 0 if failed

- exists
    * Checks to see if the user name already exists in the database (name not id)
    *

- get_categories
    * gets all top level categories (see [Categories](./categories.md) for more info)
    * returns a list of category objects
    *

- get
    * loads the user into the class from the database
    * does not return anything
    *

- get_internal_master_category
    * loads the default master category id into the user class
    * does not return anything
