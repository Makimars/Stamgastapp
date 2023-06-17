# login, register, add friend, get friends
import database

import os


def get_friends(user_id):
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
    sql = "SELECT friendship_id FROM friends WHERE requester_user_id = %s AND target_user_id = %s"
    database.cursor.execute(sql, [user_id, target_user_id])
    if len(database.cursor.fetchall) > 0:
        return

    sql = 'INSERT INTO friends (requester_user_id, target_user_id) VALUES (%s, %s);'
    database.cursor.execute(sql, [user_id, target_user_id])
    database.connection.commit()


# loads incoming friend requests
def load_friend_requests(user_id: int):
    sql = """
    SELECT friendship_id, username, user_id, profile_picture FROM
        (SELECT * FROM friends WHERE target_user_id = %s AND accepted = FALSE) AS friends
    LEFT JOIN users ON 
        friends.requester_user_id = users.user_id;
    """
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
    database.cursor.execute(sql, ["%" + pattern + "%"])
    return database.cursor.fetchall()


def set_profile_picture(user_id: int, profile_picture_filename: str):
    sql = "SELECT user_id, profile_picture FROM users WHERE user_id = %s"
    database.cursor.execute(sql, [user_id])
    result = database.cursor.fetchall()

    if len(result) > 1:
        old_file = "profile_pictures/" + result[1] + ".jpg"
        if os.path.exists(old_file):
            os.remove(old_file)

    sql = "UPDATE users SET profile_picture = %s WHERE user_id = %s"
    database.cursor.execute(sql, [profile_picture_filename, user_id])
