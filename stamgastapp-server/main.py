from flask import Flask, request, jsonify

import database, post, user

database.connection = database.get_connection()
database.cursor = database.connection.cursor()

app = Flask(__name__)


@app.route("/auth/login")
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    token = user.get_auth_token(username, password)

    return token, 200


@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user.register_new_user(username, password)

    return "success", 201


@app.route("/user/friends/<user_token>", methods=["GET"])
def get_friends(user_token):
    user_id = user.login_with_token(user_token)
    friends = user.get_friends(user_id)

    return friends, 200


@app.route("/user/friends/<user_token>", methods=["POST"])
def send_friend_request(user_token):
    user_id = user.login_with_token(user_token)
    target_user_id = request.args.get("target_user_id")

    user.send_friend_request(user_id, int(target_user_id))
    return "success", 200


@app.route("/user/friend-requests/<user_token>", methods=["GET"])
def get_friend_requests(user_token):
    user_id = user.login_with_token(user_token)
    requests = user.load_friend_requests(user_id)
    return jsonify(requests), 200


@app.route("/user/friends/<user_token>", methods=["PUT"])
def accept_friend_request(user_token):
    user_id = user.login_with_token(user_token)
    friendship_id = request.args.get("friendship_id")
    user.accept_friend_request(user_id, int(friendship_id))

    return "success", 200


@app.route("/user/friends/<user_token>", methods=["DELETE"])
def unfriend(user_token):
    user_id = user.login_with_token(user_token)
    friendship_id = request.args.get("friendship_id")
    user.delete_friendship_record(user_id, int(friendship_id))

    return "success", 200


@app.route("/user/search/<user_token>")
def search_users(user_token):
    user_id = user.login_with_token(user_token)
    params = request.args.get("params")
    results = user.search(params)

    return jsonify(results), 200


@app.route("/posts/<user_token>")
def load_posts(user_token):
    user_id = user.login_with_token(user_token)

    offset = 0
    if request.args.get("offset"):
        offset = request.args.get("offset")

    own = False
    if request.args.get("own"):
        own = True

    results = post.load_posts(user_id, own, int(offset))

    return jsonify(results), 200


# TODO
@app.route("/posts/<user_token>", methods=["DELETE"])
def delete_post(user_token):
    pass


# TODO
def load_own_posts():
    pass


@app.route("/posts/<user_token>", methods=["POST"])
def new_post(user_token):
    user_id = user.login_with_token(user_token)

    name = request.args.get("name")
    drink_type = request.args.get("type")
    volume = request.args.get("volume")
    review = request.args.get("review")
    picture = request.args.get("picture")

    if name is None:
        return "name cannot be null", 400

    post.submit_post(user_id, name, drink_type, float(volume), review, picture)

    return "success", 200


if __name__ == "__main__":
    app.run(debug=True)
