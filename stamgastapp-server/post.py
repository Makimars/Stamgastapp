# interact with posts, load and save
import os.path

from mysql.connector import MySQLConnection

import database


def submit_post(user_id: int, name: str, type: str, volume: float, review: str = "", picture: str = ""):
    max_post_length = 1000
    if len(review) > max_post_length:
        raise Exception("too long review")

    sql = 'INSERT INTO posts (user_id, name, type, volume, review, picture) VALUES (%s, %s, %s, %s, %s, %s);'
    data = (user_id, name, type, volume, review, picture)

    database.cursor.execute(sql, data)
    database.connection.commit()


# loads twenty posts starting from start of all user's friends
def load_posts(user_id: int, own: bool, start: int = 0):
    # default value
    count = 20

    if own:
        sql = """ 
            SELECT * FROM posts WHERE user_id = %s ORDER BY created_at DESC LIMIT %d OFFSET %d;
        """ % (user_id, count, start)
    else:
        # DESC assures to load the newest ones
        sql = """
            SELECT * FROM(
            
                SELECT * FROM posts RIGHT JOIN 
                    (SELECT target_user_id AS friend_user_id FROM friends WHERE requester_user_id = %d AND accepted = TRUE) AS friends1
                    ON posts.user_id = friends1.friend_user_id
                UNION
                SELECT * FROM posts RIGHT JOIN 
                    (SELECT requester_user_id AS friend_user_id FROM friends WHERE target_user_id = %d AND accepted = TRUE) AS friends2
                    ON posts.user_id = friends2.friend_user_id
            ) AS results ORDER BY created_at DESC LIMIT %d OFFSET %d;
        """ % (user_id, user_id, count, start)

    database.cursor.execute(sql)
    result = database.cursor.fetchall()

    return result


def delete_post(user_id: str, post_id: str):
    sql = "SELECT picture FROM posts WHERE user_id = %s AND post_id = %s"
    database.cursor.execute(sql, [user_id, post_id])
    result = database.cursor.fetchone()
    if result is None:
        raise Exception("post not found")
    if result[0] != "default":
        path = os.path.join("post_pictures", result[0] + ".jpg")
        if os.path.exists(path):
            os.remove(path)

    sql = "DELETE FROM posts WHERE user_id = %s AND post_id = %s"

    database.cursor.execute(sql, [user_id, post_id])
    database.connection.commit()
