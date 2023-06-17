import database, hashlib, datetime


# login
def get_auth_token(username: str, password: str):
    sql = ('select password,user_id from users where username = "%s";' % username)
    database.cursor.execute(sql)
    result = database.cursor.fetchone()

    if result[0] != hashlib.sha256(password.encode('utf-8')).hexdigest():
        raise Exception("bad password or username")

    token = hashlib.sha256((username + str(datetime.datetime.now())).encode('utf-8')).hexdigest()
    sql = ('insert into tokens (user_id, token) values (%s, "%s");' % (result[1], str(token)))

    database.cursor.execute(sql)
    database.connection.commit()

    return token  # succesfully logged in


# register
def register_new_user(username: str, password: str):
    # validate the username
    if len(username) > 20:
        raise Exception("Username too long")
    if username.__contains__(' '):
        raise Exception("Invalid username, contains space")

    # validate the password
    if len(password) > 32:
        raise Exception("Password too long")
    elif len(password) < 4:
        raise Exception("password too short")

    sql = "select * from users where username = %s;"
    database.cursor.execute(sql, [username])

    result = database.cursor.fetchall()
    if len(result) != 0:
        raise Exception("username already exists")

    sql = 'INSERT INTO users (username, password) VALUES (%s, %s);'
    database.cursor.execute(sql, (username, hashlib.sha256(password.encode('utf-8')).hexdigest()))
    database.connection.commit()


# get user_id from token and assure that the token is valid
def login_with_token(token: str):
    max_age_of_token = 365
    sql = 'SELECT user_id, created_at FROM tokens WHERE token = "%s" ORDER BY created_at DESC;' % token
    database.cursor.execute(sql)
    result = database.cursor.fetchone()
    if result is None:
        raise Exception("Invalid token")

    if len(result) != 2:
        raise Exception("Invalid token")
    else:
        user_id = result[0]
        created_at = datetime.datetime.fromisoformat(str(result[1]))

        if datetime.datetime.now() - created_at > datetime.timedelta(days=max_age_of_token):
            raise Exception("Expired token")
        else:
            return user_id
