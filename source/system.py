from source.sql import *
from source.exceptions import *
import time
from datetime import datetime, timedelta

# dbname = "Forze$default"
dbname = "forze_inventory"
import hashlib

class System:
    def __init__(self):
        self._connection = sqlConnect()
        self._cursor = sqlCursor(self._connection)
        self.sync_type_tables()

    def __dest__(self):
        sqlDisconnect(self._cursor, self._connection)

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, val):
        self._connection = val

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, val):
        self._cursor = val

    def disconnectDB(self):
        sqlDisconnect(self.cursor, self.connection)

    def add_type(self, category, item_type):
        print("System Class: Need to implement add_type")
        print("System Class {39}: "+category)
        print("System Class {40}: "+item_type)

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
        query = f"SHOW COLUMNS FROM {table}"
        rawresult = makeQuery(self, query)
        rawresult = [listAsciiSeperator(x) for x in rawresult]

        res = []
        
        for e in rawresult:
            res.append(e[0])

        return res

    #Gets all the entries in a given column
    #RETURNS: List of entries in the given column
    def get_column_items(self, table, columnName):
        query = f"SELECT `{columnName}` FROM `{table}`"
        rawresult = makeQuery(self, query)
        result = [asciiSeperator(x) for x in rawresult]
        return result

    #Gets all of the unique entries in a given column
    def get_unique_column_items(self, table, columnName):
        query = f"SELECT DISTINCT `{columnName}` FROM `{table}`"
        rawresult = makeQuery(self, query)
        print(rawresult)
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
        rawresult = makeQuery(self, query)
        result = [listAsciiSeperator(x) for x in rawresult]

        new_res = []

        for item in result:
            new_res.append({
                'id': item[0],
                'data': item[1:]
            })

        return new_res

    def get_category_table(self, category, item_type):
        orderBy = self.get_column_names(category)
        orderBy.remove("item_id")

        columnStr = ""
        for element in orderBy:
            columnStr = columnStr + element + ", "

        temp = columnStr[:-2]

        query = f"SELECT * FROM {category} WHERE `type` = '{item_type}' ORDER BY {temp}"
        rawresult = makeQuery(self, query)
        result = [listAsciiSeperator(x) for x in rawresult]

        new_res = []

        for item in result:
            new_res.append({
                'data': item
            })

        return new_res

    #Gets the list of changes that were made, and by whom
    def get_user_changes(self, itemID):
        query = f"SELECT `first_name`, `last_name`, `quantity`, `time` FROM `users` JOIN `user_changes` ON `users`.`user_id` = `user_changes`.`user_id` WHERE `user_changes`.`item_id` = {itemID}"
        rawresult = makeQuery(self, query)
        result = [listAsciiSeperator(x) for x in rawresult]
        return result

    #gets the database entry given the item ID and
    def get_entry_by_id(self, itemID):
        categories = self.get_category_list()

        for category in categories:
            res = self.get_entry_by_category_id(category, itemID)

            if len(res) != 0:
                res.append(category)
                return res

        return None

    #gets the database entry given the item ID and table
    def get_entry_by_category_id(self, table, itemID):
        query = f"SELECT * FROM `{table}` WHERE `item_id`={itemID}"
        rawresult = makeQuerySingleItem(self, query)
        result = [asciiSeperator(x) for x in rawresult]
        return result

    #Add an entry
    def add_entry(self, table, column, newValue):
        query = f"INSERT INTO `{table}` ("

        iter = 0
        for i in column:
            query += f"`{i}`, "
            # if i == 'type' and not self.check_if_type_exists(newValue[iter]):
            #     print("adding in 'add entry (L179)")
            #     system.add_to_type_table(newValue[iter])
            iter += 1

        query = query[:-2]

        query += f") VALUES ("

        for i in newValue:
            j = str(i).upper()
            query += f"'{j}', "

        query = query[:-2]

        query += ");"

        makeCommit(self, query)

    #Delete an entry
    def delete_entry(self, table, itemID):
        query = f"DELETE FROM `{table}` WHERE `item_id` = {itemID}"
        makeCommit(self, query)
        return

    #Get a list of categories
    def get_category_list(self):
        query = f"SELECT `table_name` FROM `information_schema`.`tables` WHERE `table_schema` ='{dbname}'"
        rawresult = makeQuery(self, query)
        result = [asciiSeperator(x) for x in rawresult]

        result.remove('user_changes')
        result.remove('users')
        result.remove('types')
        return result

    # #Set new entity total weight
    # def set_quantity(self, table, itemID, newWeight):
    #     query = f"UPDATE `{table}` SET `weight_total` = {newWeight} WHERE `item_id` = {itemID}"
    #     makeCommit(self._connection, self._cursor, query)
    #     return

    def add_user_entry(self, table, userID, itemID, newValues):
        entry = self.get_entry_by_category_id(table, itemID)
        curr_weight_total = entry[-1]
        curr_weight_pp = entry[-2]
        curr_quantity = float(curr_weight_total)/float(curr_weight_pp)

        new_weight_total = newValues[-1]
        new_weight_pp = newValues[-2]
        new_quantity = float(new_weight_total)/float(new_weight_pp)

        quantity_change = int(new_quantity)-int(curr_quantity)
        if quantity_change == 0:
            return
        date = datetime.now()

        query = f"INSERT INTO `user_changes` (`user_id`, `item_id`, `quantity`, `time`) VALUES ('{userID}', '{itemID}', '{quantity_change}', '{date}');"
        # print(query)
        makeCommit(self, query)

    def get_data_type_of_column(self, table, column):
        query = f"SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{table}' AND COLUMN_NAME = '{column}'"
        rawresult = makeQuerySingleItem(self, query)
        result = [asciiSeperator(x) for x in rawresult]
        return result

    #Set entry value
    def set_value(self, table, itemID, column, newValue, userID=1):
        self.add_user_entry(table, userID, itemID, newValue)
        query = f"UPDATE `{table}` SET "

        for i in range(len(column)):
            upperval = str(newValue[i]).upper()
            query += f"`{column[i]}` = \"{upperval}\", "
            # if column[i] == 'type' and not system.check_if_type_exists(upperval):
            #     print("adding in setValue")
            #     self.add_to_type_table(upperval)

        query = query[:-2]

        query += f" WHERE `item_id` = {itemID}"
        makeCommit(self, query)
        return

    ####EDIT ENTRY

    #Returns array of conditional formating values
    def get_conditional_formatting(self, type):
        print(f"Name = {type}")
        query = f"SELECT `low`, `high` FROM `types` WHERE `name` = '{type}'"
        rawresult = makeQuerySingleItem(self,query)
        print(rawresult)
        if rawresult != None and len(rawresult) != 0:
            result = [asciiSeperator(x) for x in rawresult]
            intresult = [int(result[0]), int(result[1])]
            return intresult
        else:
            raise systemException(f"Invalid conditional formatting string returned for type: {type}")
        return

    #checks credentials
    def check_credentials(self, username, password):
        query = f"SELECT * FROM `users` WHERE `username` = '{username}' AND `pw_hash` = '{password}'"
        try:
            records = makeQuerySingleItem(self,query)
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
        result = makeQuerySingleItem(self, query)
        if result == None or len(result) == 0:
            return 0
        else:
            return 1

    # Finds all of the types that are ACTUALLY in the database
    def get_type_list_manually(self):
        categories = self.get_category_list()
        types = []
        for cat in categories:
            print(cat)
            result = self.get_unique_column_items(cat, 'type')
            types.extend(result)
        return types

    # Finds all of the types that SHOULD be in the database
    def get_type_list_table(self):
        query = f"SELECT `name` FROM `types`"
        rawresult = makeQuery(self,query)
        result = [asciiSeperator(x) for x in rawresult]
        return result

    #In the case of a discrepency between the types in the database, and the types that are expected, this function syncs them
    def sync_type_tables(self):
        print("SYNCING THE TABLE")
        final_list = []
        manual = self.get_type_list_manually()
        print("MANUAL:")
        print(manual)
        auto = self.get_type_list_table()
        print("Auto:")
        print(auto)

        if auto != None:
            for man in manual:
                if man not in auto:
                    final_list.append(man)
                else:
                    auto.remove(man)

        for str in final_list:
            print("adding in sync")
            self.add_to_type_table(str)
        return

    def add_to_type_table(self, type):
        print("WHY AM I ADDING")
        query = f"INSERT INTO `types` VALUES (NULL, '{type}', NULL, '0', '0')"
        makeCommit(self, query)

    def get_type_table(self):
        query = f"SELECT `name`, `high`, `low` FROM `types`"
        result = makeQuery(self,query)
        return result

    def check_if_type_exists(self, type):
        print(f"adding {type}")
        query = f"SELECT * FROM `types` WHERE `name`='{type}'"
        result = makeQuerySingleItem(self,query)
        if result == None or len(result) == 0:
            return True
        else:
            return False

    def edit_type_table(self, type, low, high):
        for i in range(len(type)):
            query = f"UPDATE `types` SET `low` = '{low[i]}', `high` = '{high[i]}' WHERE `types`.`name` = '{type[i]}';"
            makeCommit(self,query)
        return

    def search(self, category, searchDict):
        query = f"SELECT * FROM `{category}` WHERE"
        for key in searchDict.keys():
            query += f" {key} = \"{searchDict[key]}\" AND"

        query = query[:-4]+";"

        rawresult = makeQuery(self, query)
        result = [listAsciiSeperator(x) for x in rawresult]

        new_res = []

        for item in result:
            new_res.append({
                'id': item[0],
                'data': item[1:]
            })

        return new_res