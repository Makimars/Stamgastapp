# login, register, add friend, get friends
import database

import os
import base64
import post


# creates a json object from ordered list of user attributes
# user_id, username, created_at, profile_picture
def load_user(user_record):
    user = {"user_id": user_record[0], "username": user_record[1], "created_At": user_record[2]}

    if user_record[3] == "default" or user_record[3] is None:
        user["profile_picture"] = "default"
    else:
        user["profile_picture"] = user_record[3]
    return user


def get_friends(user_id):
    sql = """
    SELECT user_id, username, created_at, profile_picture FROM(
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
    users = []
    for record in database.cursor.fetchall():
        users.append(load_user(record))
    return users


def send_friend_request(user_id: int, target_user_id: int):
    sql = "SELECT friendship_id FROM friends WHERE requester_user_id = %s AND target_user_id = %s"
    database.cursor.execute(sql, [user_id, target_user_id])
    if len(database.cursor.fetchall()) > 0:
        return

    sql = 'INSERT INTO friends (requester_user_id, target_user_id) VALUES (%s, %s);'
    database.cursor.execute(sql, [user_id, target_user_id])
    database.connection.commit()


# loads incoming friend requests
def load_friend_requests(user_id: int):
    sql = """
    SELECT user_id, username, created_at, profile_picture, friendship_id FROM
        (SELECT * FROM friends WHERE target_user_id = %s AND accepted = FALSE) AS friends
    LEFT JOIN users ON 
        friends.requester_user_id = users.user_id;
    """

    database.cursor.execute(sql, [user_id])
    results = database.cursor.fetchall()
    friends = []

    for i in range(len(results)):
        user = load_user(results[i])
        user['friendship_id'] = results[i][4]
        friends.append(user)

    return friends


# accepts a friend request
def accept_friend_request(user_id: int, friendship_id: int):
    sql = 'UPDATE friends SET accepted = TRUE WHERE target_user_id = %s AND friendship_id = %s;'
    database.cursor.execute(sql, [user_id, friendship_id])
    database.connection.commit()


# deletes the friendship record (unfriends)
def delete_friendship_record(user_id: int, target_user_id: int):
    sql = 'DELETE FROM friends WHERE ' \
          '(requester_user_id = %s AND target_user_id = %s) OR (requester_user_id = %s AND target_user_id = %s)'

    database.cursor.execute(sql, [user_id, target_user_id, target_user_id, user_id])
    database.connection.commit()


# searches people by username
def search(pattern: str):
    sql = 'SELECT user_id, username, created_at, profile_picture FROM users WHERE username LIKE %s'
    database.cursor.execute(sql, ["%" + pattern + "%"])
    users = []
    for record in database.cursor.fetchall():
        users.append(load_user(record))
    return users


def set_profile_picture(user_id: int, profile_picture_filename: str):
    sql = "SELECT user_id, profile_picture FROM users WHERE user_id = %s"
    database.cursor.execute(sql, [user_id])
    result = database.cursor.fetchone()

    if result[1] is not None and result[1] != "default":
        old_file = os.path.join("profile_pictures", (result[1] + ".jpg"))
        if os.path.exists(old_file):
            os.remove(old_file)

    sql = "UPDATE users SET profile_picture = %s WHERE user_id = %s"
    database.cursor.execute(sql, [profile_picture_filename, user_id])
    database.connection.commit()


def get_user_info(user_id):
    sql = "SELECT user_id, username, created_at, profile_picture FROM users WHERE user_id = %s"
    database.cursor.execute(sql, [user_id])

    user = load_user(database.cursor.fetchone())
    return user


def delete_user(user_id):
    sql = "SELECT post_id FROM posts WHERE user_id = %s"
    database.cursor.execute(sql, [user_id])
    post_list = database.cursor.fetchall()

    # delete all posts
    for one_post in post_list:
        post.delete_post(user_id, one_post[0])

    sql = "DELETE FROM friends WHERE target_user_id = %s OR requester_user_id = %s"
    database.cursor.execute(sql, [user_id, user_id])

    # deletes the current profile picture
    set_profile_picture(user_id, "default")

    sql = "DELETE FROM users WHERE user_id = %d"
    database.cursor.execute(sql, [user_id])

    database.connection.commit()
    return
