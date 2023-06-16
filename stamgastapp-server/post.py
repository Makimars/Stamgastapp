# interact with posts, load and save
from mysql.connector import MySQLConnection

import database


def submit_post(user_id: int, brand: str, product: str, volume: float, review: str = ""):
    max_post_length = 500
    if len(review) > max_post_length:
        print("too long review")
        raise Exception()

    sql = 'INSERT INTO posts (user_id, brand, product, volume, review) VALUES (%s, %s, %s, %s, %s);'
    data = (user_id, brand, product, volume, review)

    database.cursor.execute(sql, data)
    database.connection.commit()


# loads twenty posts starting from start of all user's friends
def load_posts(user_id: int, start: int = 0):
    # default value
    count = 20

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

