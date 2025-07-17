# Categories

The Category is the logical account for money storage and transfer.  
The Category is a hierarchy of 3 tiers (our logical limit, in theory we could have infinite tiers)

The Category class has the following attributes:

- database (Database Object)
    * The database object, passed in so we can run tests with a theoretical database.

- name (String)
    * the name of the category

- budget_value (int)
    * The logical value of stored money (see [Transactions](./transactions.md) for why we chose int over float or double)
    * (NOT YET IMPLEMENTED) if this is a parent category, Should be a summed value of all child budget_values

- id (int)
    * The ID of the category as stored in the database

- children (List of Category Objects)
    * used to manage the child categories.

- parent (Category Object)
    * used to manage the Parent Category

- user_id (int)
    * the ID of the user as stored in the database

The Category class has the following methods:

- add
    * Adds the category to the database
    * Returns category id (INT) if successful

- get_default_category
    * Sets the parent category to the internal master category of the user.
    * does not return

- get_id
    * sets the id attribute of the category (or 0 if failed)

- get_name
    * sets the name attribute of the category (or 'unknown' if failed)

- get_children
    * Gets from the database all children of the category, 
    * for each child, creates a Category object and adds that object to the children attribute.

- get
    * Gets the information of a category from the database
    * returns the database resuults
