from source.sql import *
from source.exceptions import *
import time
from datetime import datetime, timedelta
import hashlib

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

    def disconnectDB(self):
        sqlDisconnect(self.cursor, self.connection)

    #Gets all of the column names and prettifies them...
    #RETURNS: list of the column names
    def get_pretty_column_names(self, table):
        raw_columns = self.get_column_names(table)

        pretty_columns = []
        for k in raw_columns:
            k = k.split("_")

            for i in range(len(k)):
                k[i] = k[i].capitalize()

            k = " ".join(k)

            pretty_columns.append(k)

        return pretty_columns


    #Gets all of the column names
    #RETURNS: list of the column names
    def get_column_names(self, table):
        query = f"select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{table}'"
        rawresult = makeQuery(self._cursor, query)
        result = [asciiSeperator(x) for x in rawresult]

        result.remove('item_id')

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

    def check_auth(self, username, password, secret_key):
        remembermeHash = username + password + secret_key
        remembermeHash = hashlib.sha1(remembermeHash.encode())
        remembermeHash = remembermeHash.hexdigest()

        # Check if account exists using MySQL

        passwordHash = password + secret_key
        passwordHash = hashlib.sha1(passwordHash.encode())
        passwordHash = passwordHash.hexdigest()

        account = self.check_credentials(username, passwordHash)

        if account != None:
            return [remembermeHash, account[0]]

        return None

    #Sorts the dataset of a given table by the columns given
    def sort_by_columns(self, table, order):
        columnStr = ""
        for element in order:
            columnStr = columnStr + element + ", "

        temp = columnStr[:-2]

        query = f"SELECT * FROM {table} ORDER BY {temp}"
        rawresult = makeQuery(self._cursor, query)
        result = [listAsciiSeperator(x) for x in rawresult]

        new_res = []

        for item in result:
            new_res.append({
                'id': item[0],
                'data': item[1:]
            })

        return new_res

    def get_category_table(self, category, item_type, orderBy):
        columnStr = ""
        for element in orderBy:
            columnStr = columnStr + element + ", "

        temp = columnStr[:-2]

        query = f"SELECT * FROM {category} WHERE `type` = '{item_type}' ORDER BY {temp}"
        rawresult = makeQuery(self._cursor, query)
        result = [listAsciiSeperator(x) for x in rawresult]

        new_res = []

        for item in result:
            new_res.append({
                'id': item[0],
                'data': item[1:]
            })

        return new_res

    #Gets the list of changes that were made, and by whom
    def get_user_changes(self, itemID):
        query = f"SELECT `first_name`, `last_name`, `quantity`, `time` FROM `users` JOIN `user_changes` ON `users`.`user_id` = `user_changes`.`user_id` WHERE `user_changes`.`item_id` = {itemID}"
        rawresult = makeQuery(self._cursor, query)
        result = [listAsciiSeperator(x) for x in rawresult]
        return result

    #gets the database entry given the item ID
    def get_entry_by_id(self, table, itemID):
        query = f"SELECT * FROM `{table}` WHERE `item_id`={itemID}"
        rawresult = makeQuerySingleItem(self._cursor, query)
        result = [asciiSeperator(x) for x in rawresult]
        return result

    #Add an entry
    def add_entry(self, table, column, newValue):
        query = f"INSERT INTO `{table}` ("

        for i in column:
            query += f"`{i}`, "

        query = query[:-2]

        query += f") VALUES ("

        for i in newValue:
            query += f"'{i}', "

        query = query[:-2]

        query += ");"

        makeCommit(self._connection, self._cursor, query)

    #Delete an entry
    def delete_entry(self, table, itemID):
        query = f"DELETE FROM `{table}` WHERE `item_id` = {itemID}"
        makeCommit(self._connection, self._cursor, query)
        return

    # #Set new entity total weight
    # def set_quantity(self, table, itemID, newWeight):
    #     query = f"UPDATE `{table}` SET `weight_total` = {newWeight} WHERE `item_id` = {itemID}"
    #     makeCommit(self._connection, self._cursor, query)
    #     return

    def add_user_entry(self, table, userID, itemID, newValues):
        entry = self.get_entry_by_id(table, itemID)
        curr_weight_total = entry[-1]
        curr_weight_pp = entry[-2]
        curr_quantity = float(curr_weight_total)/float(curr_weight_pp)

        new_weight_total = newValues[-1]
        new_weight_pp = newValues[-2]
        new_quantity = float(new_weight_total)/float(new_weight_pp)

        quantity_change = int(new_quantity-curr_quantity)
        if quantity_change == 0:
            return
        date = datetime.now()

        query = f"INSERT INTO `user_changes` (`user_id`, `item_id`, `quantity`, `time`) VALUES ('{userID}', '{itemID}', '{quantity_change}', '{date}');"
        # print(query)
        makeCommit(self._connection, self._cursor, query)

    def get_data_type_of_column(self, table, column):
        query = f"SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{table}' AND COLUMN_NAME = '{column}'"
        rawresult = makeQuerySingleItem(self._cursor, query)
        result = [asciiSeperator(x) for x in rawresult]
        return result

    #Set entry value
    def set_value(self, table, itemID, column, newValue, userID=1):
        self.add_user_entry(table, userID, itemID, newValue)
        query = f"UPDATE `{table}` SET "

        for i in range(len(column)):
            query += f"`{column[i]}` = \"{newValue[i]}\", "

        query = query[:-2]

        query += f" WHERE `item_id` = {itemID}"
        # print(query)
        makeCommit(self._connection, self._cursor, query)
        return

    ####EDIT ENTRY

    #Returns array of conditional formating values
    def get_conditional_formatting(self, ):

        return

    #checks credentials
    def check_credentials(self, username, password):
        query = f"SELECT * FROM `users` WHERE `username` = '{username}' AND `pw_hash` = '{password}'"
        try:
            self._cursor.execute(query)
            records = self._cursor.fetchone()
            if records != None:
                result = [asciiSeperator(x) for x in records]
            else:
                result = None
        except Exception as err:
            raise builtInException(err)
        return result

    #checks account existance. return 1 if exists already.
    def checkExistance(self, username):
        query = f"SELECT * FROM `users` WHERE `username` = '{username}'"
        result = makeQuerySingleItem(self._cursor, query)
        if result == None:
            return 0
        else:
            return 1

sys = System()