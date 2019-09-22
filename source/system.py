from sql import *
from exceptions import *
import time

class System:
    def __init__(self):
        self._connection = sqlConnect()
        self._cursor = sqlCursor(self._connection)

    def __dest__(self):
        sqlDisconnect(self._cursor, self._connection)
        
    @property
    def connection(self):
        return self._connection

    @property
    def cursor(self):
        return self._cursor 

    #Gets all of the column names
    #RETURNS: list of the column names 
    def get_column_names(self, table):
        query = f"select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{table}'"
        rawresult = makeQuery(self._cursor, query)
        result = [asciiSeperator(x) for x in rawresult]
        return result

    #Gets all the entries in a given column
    #RETURNS: List of entries in the given column
    def get_column_items(self, table, columnName):
        query = f"SELECT `{columnName}` FROM `{table}`"
        rawresult = makeQuery(self._cursor, query)
        result = [asciiSeperator(x) for x in rawresult]
        return result
    
    #Gets all of the unique entries in a given column
    def get_unique_column_items(self, table, columnName):
        query = f"SELECT DISTINCT `{columnName}` FROM `{table}`"
        rawresult = makeQuery(self._cursor, query)
        result = [asciiSeperator(x) for x in rawresult]
        return result
    
    #Sorts the dataset of a given table by the columns given
    def sort_by_columns(self, table, order):
        columnStr = ""
        for element in order:
            columnStr = columnStr + element + ", "
        query = f"SELECT * FROM {table} ORDER BY {columnStr}"
        rawresult = makeQuery(self._cursor, query)
        result = [listAsciiSeperator(x) for x in rawresult]
        return result
    
    #Gets the list of changes that were made, and by whom
    def get_user_changes(self, itemID):
        query = f"SELECT `first_name`, `last_name`, `quantity`, `time` FROM `users` JOIN `user_changes` ON `users`.`user_id` = `user_changes`.`user_id` WHERE `user_changes`.`item_id` = {itemID}"
        rawresult = makeQuery(self._cursor, query)
        result = [listAsciiSeperator(x) for x in rawresult]
        return result

    #gets the database entry given the item ID
    def get_entry_by_id(self, table, itemID):
        query = f"SELECT * FROM `{table}` WHERE `item_id`={itemID}"
        rawresult = makeQuery(self._cursor, query)
        result = [asciiSeperator(x) for x in rawresult]
        return result
    
    #Add an entry
    def add_entry(self, table, typ, diameter, strength, size, w_pp, w_total, storage):
        query = f"INSERT INTO `{table}` (`item_id`, `type`, `diameter`, `strength`, `size`, `weight_pp`, `weight_total`, `storage`) VALUES (NULL, '{typ}', '{diameter}', '{strength}', '{size}', '{w_pp}', '{w_total}', '{storage}');"
        makeQuery(self._cursor, query)
        return
    
    #Delete an entry
    def delete_entry(self, ):

        return
    
    #Increase quantity
    def add_quantity(self, ):

        return
    
    #Decrease quantity
    def dec_quantity(self, ):

        return
    
    #Returns array of conditional formating values
    def get_conditional_formatting(self, ):

        return
    
#print(get_column_names("Bolts"))
#print(get_column_items("Bolts","item_id"))
#print('speed test')
sys = System()
sys.add_entry("Bolts", "Allan Bolt", "M6", 12.9, 12.9, 5.4, 5363, 500)
