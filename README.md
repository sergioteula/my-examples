# shelveSQLite-class-example
This is an example of persistent Python classes using both Shelve and SQLite. There is a superclass named Persistent that saves the subclasses on a Shelve and loads the previous status on each init. On the other hand, some classes use SQLite to save the data and get it for later use.
