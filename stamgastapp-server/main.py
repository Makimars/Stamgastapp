import datetime
import email.charset

import flask
from flask import Flask, request, jsonify
import os
import hashlib
from PIL import Image
import base64

import database
import post
import user
import auth

database.connection = database.get_connection()
database.cursor = database.connection.cursor()

app = Flask(__name__)


def try_to_login_with_token(user_token):
    try:
        # this needs sql injection prevention
        for char in user_token:
            if char not in '1234567890abcdef':
                flask.abort(401)
        return auth.login_with_token(user_token)
    except Exception:
        flask.abort(401)


def username_password_checker(input: str):
    disallowed_chars = [' ', '*', ';', '$', '%']
    if any(c in input for c in disallowed_chars):
        flask.abort(400)
    else:
        return input


def filter_sql_str_argument(argument: str):
    argument.replace(' ', '')
    argument.replace('*', '')
    argument.replace(';', '')
    return argument


@app.route("/auth/login")
def login():
    data = request.get_json()
    try:
        username = username_password_checker(data["username"])
        password = username_password_checker(data["password"])
        token = auth.get_auth_token(username, password)
    except Exception as e:
        return str(e.args), 400

    return token, 200


@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    try:
        username = username_password_checker(data["username"])
        password = username_password_checker(data["password"])
        auth.register_new_user(username, password)
    except Exception as e:
        return str(e.args), 400

    return "success", 201


@app.route("/user/friends/<user_token>", methods=["GET"])
def get_friends(user_token):
    try_to_login_with_token(user_token)
    user_id = try_to_login_with_token(user_token)
    friends = user.get_friends(user_id)

    return friends, 200


@app.route("/user/friends/<user_token>", methods=["POST"])
def send_friend_request(user_token):
    user_id = try_to_login_with_token(user_token)
    try:
        target_user_id = int(request.args.get("target_user_id"))
    except TypeError:
        return "invalid target user", 400
    except ValueError:
        return "invalid target user", 400
    if user_id == target_user_id:
        return "cannot send to yourself", 400

    user.send_friend_request(user_id, target_user_id)
    return "success", 200


@app.route("/user/friend-requests/<user_token>", methods=["GET"])
def get_friend_requests(user_token):
    user_id = try_to_login_with_token(user_token)
    requests = user.load_friend_requests(user_id)
    return jsonify(requests), 200


@app.route("/user/friends/<user_token>", methods=["PUT"])
def accept_friend_request(user_token):
    user_id = try_to_login_with_token(user_token)
    try:
        friendship_id = int(request.args.get("friendship_id"))
    except TypeError:
        return "invalid target user", 400
    except ValueError:
        return "invalid target user", 400

    user.accept_friend_request(user_id, friendship_id)

    return "success", 200


@app.route("/user/friends/<user_token>", methods=["DELETE"])
def unfriend(user_token):
    user_id = try_to_login_with_token(user_token)
    try:
        target_user = int(request.args.get("target_user_id"))
    except TypeError:
        return "invalid target user", 400
    except ValueError:
        return "invalid target user", 400

    user.delete_friendship_record(user_id, target_user)

    return "success", 200


@app.route("/user/<user_token>")
def get_user_info(user_token):
    try_to_login_with_token(user_token)

    try:
        user_to_get = int(request.args.get("user_id"))
    except TypeError:
        return "invalid target user", 400
    except ValueError:
        return "invalid target user", 400

    return jsonify(user.get_user_info(user_to_get)), 200


@app.route("/user/profile-picture/<user_token>")
def get_profile_picture(user_token):
    try_to_login_with_token(user_token)
    picture_to_get = request.args.get("filename")
    if picture_to_get is None:
        return "invalid filename", 400
    if len(picture_to_get) is not 64 or picture_to_get.__contains__('*') or picture_to_get.__contains__('/'):
        return "invalid filename", 400

    filename = os.path.join("profile_pictures", picture_to_get + ".jpg")
    if not os.path.exists(filename):
        return "file not found", 400
    else:
        try:
            picture = str(base64.standard_b64encode(open(filename, 'rb').read()))
            return picture, 200
        except Exception:
            return "smth went wrong", 500


@app.route("/user/search/<user_token>")
def search_users(user_token):
    try_to_login_with_token(user_token)
    params = request.args.get("params")
    if params is None:
        return "no search params", 400
    if len(params) < 3:
        return "too short params", 400

    results = user.search(username_password_checker(params))

    return jsonify(results), 200


@app.route("/posts/<user_token>")
def load_posts(user_token):
    user_id = try_to_login_with_token(user_token)

    offset = 0
    if request.args.get("offset"):
        try:
            offset = int(request.args.get("offset"))
        except ValueError:
            return "invalid offset value", 400
        except TypeError:
            return "invalid offset value", 400

    own = False
    if request.args.get("own"):
        own = True

    return jsonify(post.load_posts(user_id, own, offset)), 200


@app.route("/posts/<user_token>", methods=["DELETE"])
def delete_post(user_token):
    user_id = try_to_login_with_token(user_token)
    if not request.args.get("post_id"):
        return "no post_id", 400

    try:
        post_id = int(request.args.get("post_id"))
    except ValueError:
        return "invalid post_id", 400
    except TypeError:
        return "invalid post_id", 400

    try:
        post.delete_post(user_id, post_id)
        return "success", 200
    except Exception as ex:
        if ex.args == "post not found":
            return ex.args, 200

    return "request failed", 500


@app.route("/posts/<user_token>", methods=["POST"])
def new_post(user_token):
    user_id = try_to_login_with_token(user_token)

    name = request.args.get("name")
    if name is None:
        return "name cannot be null", 400

    try:
        drink_type = int(request.args.get("type"))
        if drink_type is None:
            drink_type = 0
        volume = float(request.args.get("volume"))
    except ValueError:
        return "invalid type or volume", 400
    except TypeError:
        return "invalid type or volume", 400

    review = request.args.get("review")
    picture_filename = "default"

    if request.content_type == "image/jpeg":
        # max file size 500kb
        if request.content_length > 500000:
            return "file too big", 400

        picture_filename = hashlib.sha256((str(datetime.datetime.now()) + str(user_id)).encode("utf-8")).hexdigest()
        picture_filename_with_path = os.path.join("post_pictures", picture_filename)
        tmp_file = open(picture_filename_with_path, "wb")
        tmp_file.write(request.get_data())

        image = Image.open(picture_filename_with_path)
        try:
            image.verify()
        except Exception:
            os.remove(picture_filename_with_path)
            return "corrupted picture", 400

        image.thumbnail((1024, 1536), Image.ANTIALIAS)
        image.save(picture_filename_with_path + ".jpg", 'JPEG', quality=70)
        os.remove(picture_filename_with_path)

    try:
        post.submit_post(user_id, filter_sql_str_argument(name), drink_type, volume, filter_sql_str_argument(review),
                         picture_filename)
    except Exception:
        return "too long review", 400

    return "success", 200


@app.route("/user/profile-picture/<user_token>", methods=["POST"])
def set_profile_picture(user_token):
    user_id = try_to_login_with_token(user_token)

    if request.content_type != "image/jpeg":
        return "wrong format", 400

    filename_construction = str(datetime.datetime.now()) + str(user_id)
    filename = hashlib.sha256(filename_construction.encode('utf-8')).hexdigest()
    filename_with_path = os.path.join("profile_pictures", filename)

    temp_file = open(filename_with_path, "wb")
    temp_file.write(request.get_data())

    image = Image.open(filename_with_path)
    try:
        image.verify()
    except Exception:
        os.remove(filename_with_path)
        return "corrupted picture", 400

    image.thumbnail((512, 512), Image.ANTIALIAS)
    image.save(filename_with_path + ".jpg", 'JPEG', quality=70)

    os.remove(filename_with_path)

    user.set_profile_picture(user_id, filename)

    return filename, 201


if __name__ == "__main__":
    f = open("config", "r")
    lines = f.readlines()
    server_address = lines[4].strip()
    app.config['SERVER_NAME'] = server_address
    app.run(debug=True)
