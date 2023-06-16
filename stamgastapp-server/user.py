# login, register, add friend, get friends
import database

import hashlib
import datetime


# login
def get_auth_token(username: str, password: str):
    sql = ('select password,user_id from users where username = "%s";' % username)
    database.cursor.execute(sql)
    result = database.cursor.fetchone()

    if result['password'] != password:
        print("bad password or username")
        raise Exception

    token = hashlib.md5((username + str(datetime.datetime.now())).encode('utf-8')).hexdigest()
    sql = ('insert into tokens (user_id, token) values (%s, "%s");' % (result['user_id'], str(token)))

    print(sql)

    database.cursor.execute(sql)
    database.connection.commit()

    return token  # succesfully logged in


# register
def register_new_user(username: str, password: str):
    # validate the username
    if len(username) > 20:
        print("Username too long")
        exit()
    if username.__contains__(' '):
        print("Invalid username, contains space")
        exit()

    # validate the password
    if len(password) > 32:
        print("Password too long")
        exit()
    elif len(password) < 4:
        print("password too short")
        exit()

    sql = "select * from users where username = %s;"
    database.cursor.execute(sql, [username])

    result = database.cursor.fetchall()
    if len(result) != 0:
        print("username already exists")
        exit()

    sql = 'INSERT INTO users (username, password) VALUES (%s, %s);'
    database.cursor.execute(sql, (username, password))
    database.connection.commit()


# get user_id from token and assure that the token is valid
def login_with_token(token: str):
    sql = 'SELECT user_id, created_at FROM tokens WHERE token = "%s" ORDER BY created_at DESC;' % token
    database.cursor.execute(sql)
    result = database.cursor.fetchone()

    if len(result) != 2:
        raise Exception("Invalid token")
    else:
        user_id = result['user_id']
        created_at = datetime.datetime.fromisoformat(str(result['created_at']))

        if datetime.datetime.now() - created_at > datetime.timedelta(days=365):
            raise Exception("Expired token")
        else:
            return user_id


def load_friends(user_id):
    sql = """
    SELECT username, profile_picture, created_at FROM(
            SELECT * FROM users RIGHT JOIN 
                (SELECT target_user_id AS friend_user_id FROM friends WHERE requester_user_id = %s AND accepted = TRUE) AS friends1
                ON users.user_id = friends1.friend_user_id
            UNION
            SELECT * FROM users RIGHT JOIN 
                (SELECT requester_user_id AS friend_user_id FROM friends WHERE target_user_id = %s AND accepted = TRUE) AS friends2
                ON users.user_id = friends2.friend_user_id
        ) AS results ORDER BY created_at DESC;
    """
    database.cursor.execute(sql, [user_id, user_id])
    return database.cursor.fetchall()


def send_friend_request(user_id: int, target_user_id: int):
    sql = 'INSERT INTO friends (requester_user_id, target_user_id) VALUES (%s, %s);'
    database.cursor.execute(sql, [user_id, target_user_id])
    database.connection.commit()


# loads incoming friend requests
def load_friend_requests(user_id: int):
    sql = 'SELECT * FROM friends WHERE target_user_id = %s AND accepted = FALSE;'
    database.cursor.execute(sql, [user_id])
    return database.cursor.fetchall()


# accepts a friend request
def accept_friend_request(user_id: int, friendship_id: int):
    sql = 'UPDATE friends SET accepted = TRUE WHERE target_user_id = %s AND friendship_id = %s;'
    database.cursor.execute(sql, [user_id, friendship_id])
    database.connection.commit()


# deletes the friendship record (unfriends)
def delete_friendship_record(user_id: int, friendship_id: int):
    sql = 'DELETE FROM friends WHERE friendship_id = %s'

    database.cursor.execute(sql, [friendship_id])
    database.connection.commit()


# searches people by username
def search(pattern: str):
    sql = 'SELECT user_id, username, profile_picture FROM users WHERE username LIKE %s'
    database.cursor.execute(sql, ["%"+pattern+"%"])
    return database.cursor.fetchall()
