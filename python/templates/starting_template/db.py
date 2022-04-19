import mysql.connector.pooling

from operator import itemgetter
from re import fullmatch
from werkzeug.security import check_password_hash

def createPool(poolData):
    poolName, host, port, user, password, db = itemgetter('poolName', 'host', 'port', 'user', 'password', 'db')(poolData)

    try:
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=poolName,
            pool_reset_session=True,
            pool_size=4,
            host=host,
            port=port,
            user=user,
            password=password,
            db=db
        )
    except:
        return False

    return pool


def query(cursor, column, table):
    try:
        response = cursor.execute(f'SELECT {column} FROM {table}')
        response = cursor.fetchall()
    except:
        return False
    else:
	    return response


def getUsername(cursor, userId):
    try:
        username = cursor.execute(f"SELECT username FROM users WHERE id = '{userId}'")
        username = cursor.fetchone()[0]
    except:
        return False

    return username


def validateUser(email, user, password, passRegEx, session, cursor, connection):
    condition = 'email' if email == True else 'username'

    try:
        userDB = cursor.execute(f"SELECT id, hash FROM users WHERE {condition} = '{user}'")
        userDB = cursor.fetchall()
        connection.close()
    except:
        message = 'An error has occurred while establishing a connection with the database. Please, try again.'
        return False, message

    message = 'Username and/or password are invalid. Please, try again.'
    if userDB:
        # Check if password is valid or not
        if not fullmatch(passRegEx, password):
            return False, message

        checkPassword = check_password_hash(userDB[0][1], password)
        if checkPassword:
            session["userId"] = userDB[0][0]
            return True

    return False, message


def getProfile(cursor, userId):
    try:
        picDirectory = cursor.execute(f"SELECT profilePicDir, bannerPicDir FROM users WHERE id = '{userId}'")
        picDirectory = cursor.fetchall()
    except:
        return False

    return picDirectory