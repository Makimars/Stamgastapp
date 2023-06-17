import database, post, user
import json
database.connection = database.get_connection()
database.cursor = database.connection.cursor()

# print(get_auth_token("hana_molodka", "pass"))
# print(login_with_token("c41541c0fe6d9d25f478f00448b34293"))
# user.register_new_user("jan_bodlak", "pokus")

# user.send_friend_request(3, 1)
# print(user.load_friend_requests(2))
# user.accept_friend_invite(1,3)

# post.submit_post(3,"birrel", "plechovka", 0.3)
# print(post.load_posts(1, False))
# print(user.get_friends(3))

# print(user.search("han"))

# database.cursor.execute("select * from users")
# print(json.dumps(database.cursor.fetchall()))
# print(json.dumps(database.cursor.description))

print(user.get_friends(2))
