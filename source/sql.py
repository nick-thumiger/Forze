import mysql.connector
from mysql.connector import Error
from exceptions import *
from datetime import datetime

#Establishes a connection to the SQL hosting site
def sqlConnect():
    connection = mysql.connector.connect(host='db4free.net', database='forze_inventory', user='nijaiki', password='NiJaiki2019')
    
    if (connection == None):
        raise mixedException("sqlConnect(): could not connect to server", "Error. A connection to the server could not be established. Please try later, or contact support.")

    return connection

#Establishes a connection to the relevant database, and generates a cursor
def sqlCursor(connection):
    if (connection.is_connected()):
        cursor = connection.cursor()
    if cursor == None:
        raise mixedException("sqlCursor(): could not instantiate cursor", "Error. A connection to the server could not be established. Please try later, or contact support.")
    return cursor

#Closes the connection to the SQL server
def sqlDisconnect(cursor, connection):
    if (connection.is_connected()):
        cursor.close()
        connection.close()
    return

#Make an SQL Query
def makeQuery(cursor, query):
    try:
        cursor.execute(query)
        records = cursor.fetchall()
    except Exception as err:
        raise builtInException(err)
    return records

#Make an SQL commit
def makeCommit(connection, cursor, query):
    try:
        cursor.execute(query)
        connection.commit()
    except Exception as err:
        raise builtInException(err)
    return

#removes SQL seperators and formatters from outputted string data
def asciiSeperator(instr):
    outstr = ""
    for c in str(instr):
        if (ord(c) >= 65 and ord(c) <= 90) or (ord(c) >= 97 and ord(c) <= 122) or (ord(c) >= 48 and ord(c) <= 57) or ord(c) == 95 or ord(c) == 46 or ord(c) == 32:
            outstr = outstr + c
    return outstr

#removes SQL seperators and formatters from outputted array data
def listAsciiSeperator(arr):
    lis = []
    for string in arr:
        lis.append(asciiSeperator(string))
    return lis
