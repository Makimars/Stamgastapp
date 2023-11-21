from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
from hashlib import sha256
from base64 import standard_b64decode, standard_b64encode
from PIL import Image
from datetime import datetime
import os

import post
import user
import auth


try:
    import database
except Exception as ex:
    print(ex.args)
    raise HTTPException(500) from ex

if not os.path.exists("profile_pictures"):
    os.makedirs("profile_pictures")
if not os.path.exists("post_pictures"):
    os.makedirs("post_pictures")

app = FastAPI()


def try_to_login_with_token(user_token):
    try:
        # this needs sql injection prevention
        for char in user_token:
            if char not in '1234567890abcdef':
                raise HTTPException(401)
        return auth.login_with_token(user_token)
    except Exception as e:
        raise HTTPException(401) from e


def username_password_checker(input_string: str):
    disallowed_chars = [' ', '*', ';']
    if any(c in input_string for c in disallowed_chars):
        raise HTTPException(400)

    return input_string


def filter_sql_str_argument(argument: str):
    argument.replace(' ', '')
    argument.replace('*', '')
    argument.replace(';', '')
    return argument


class UserData(BaseModel):
    username: str
    password: str


@app.get("/auth/login")
def login(data: UserData):
    try:
        username = username_password_checker(data.username)
        password = username_password_checker(data.password)
        token = auth.get_auth_token(username, password)
    except Exception as e:
        raise HTTPException(400, e.args) from e

    return token


@app.post("/auth/register")
def register(data: UserData):
    try:
        username = username_password_checker(data.username)
        password = username_password_checker(data.password)
        auth.register_new_user(username, password)
    except Exception as e:
        raise HTTPException(400, e.args) from e

    return "success"


@app.get("/user/friends/{user_token}")
def get_friends(user_token: str):
    try_to_login_with_token(user_token)
    user_id = try_to_login_with_token(user_token)
    friends = user.get_friends(user_id)

    return friends, 200


@app.post("/user/friends/{user_token}")
def send_friend_request(user_token: str, target_user_id: int):
    user_id = try_to_login_with_token(user_token)
    if user_id == target_user_id:
        raise HTTPException(400, "cannot target yourself")

    user.send_friend_request(user_id, target_user_id)
    return "success"


@app.get("/user/friend-requests/{user_token}")
def get_friend_requests(user_token: str):
    user_id = try_to_login_with_token(user_token)
    requests = user.load_friend_requests(user_id)
    return requests


@app.put("/user/friends/{user_token}")
def accept_friend_request(user_token: str, friendship_id: int):
    user_id = try_to_login_with_token(user_token)
    user.accept_friend_request(user_id, friendship_id)
    return "success"


@app.delete("/user/friends/{user_token}")
def unfriend(user_token: str, target_user_id: int):
    user_id = try_to_login_with_token(user_token)
    user.delete_friendship_record(user_id, target_user_id)
    return "success"


@app.get("/user/{user_token}")
def get_user_info(user_token, user_id: int):
    try_to_login_with_token(user_token)
    return user.get_user_info(user_id)


@app.get("/user/profile-picture/{user_token}")
def get_profile_picture(user_token: str, filename: str):
    try_to_login_with_token(user_token)
    if len(filename) != 64 or filename.__contains__('*') or filename.__contains__('/'):
        raise HTTPException(400, "Invalid filename")

    full_filename = os.path.join("profile_pictures", filename + ".jpg")
    if not os.path.exists(full_filename):
        raise HTTPException(400, "file not found")

    try:
        with open(full_filename, 'rb') as file:
            picture = str(standard_b64encode(file.read()))
        return picture
    except Exception as e:
        raise HTTPException(500, "smth went wrong") from e


@app.get("/user/search/{user_token}")
def search_users(user_token: str, params: str):
    try_to_login_with_token(user_token)
    if len(params) < 3:
        raise HTTPException(400, "too short search params")
    results = user.search(username_password_checker(params))
    return results


@app.get("/posts/{user_token}")
def load_posts(user_token: str, offset: int | None, own: bool | None):
    user_id = try_to_login_with_token(user_token)

    if offset is None:
        offset = 0
    if own is None:
        own = False

    return post.load_posts(user_id, own, offset)


@app.delete("/posts/{user_token}")
def delete_post(user_token: str, post_id: int):
    user_id = try_to_login_with_token(user_token)
    try:
        post.delete_post(user_id, post_id)
        return "success"
    except Exception as ex:
        if ex.args == "post not found":
            raise HTTPException(400, "post not found") from ex
        raise HTTPException(500, "request failed") from ex


class Post(BaseModel):
    name: str
    type: int | None
    volume: float | None
    review: str | None
    picture: str | None


@app.post("/posts/{user_token}")
def new_post(user_token, post_data: Post):
    user_id = try_to_login_with_token(user_token)
    picture_filename = "default"

    if post_data.picture is not None:
        picture_filename = sha256((str(datetime.now()) + str(user_id)).encode("utf-8")).hexdigest()
        picture_filename_with_path = os.path.join("post_pictures", picture_filename)
        try:
            with open(picture_filename_with_path, "wb") as tmp_file:
                tmp_file.write(standard_b64decode(post_data.picture))
        except Exception as e:
            raise HTTPException(400, "invalid file") from e

        try:
            with Image.open(picture_filename_with_path) as image:
                image.verify()
        except Exception as e:
            os.remove(picture_filename_with_path)
            return HTTPException(400, "corrupted picture")

        with Image.open(picture_filename_with_path) as image:
            image.thumbnail((1024, 1536), Image.ANTIALIAS)
            image.save(picture_filename_with_path + ".jpg", 'JPEG', quality=70)
            os.remove(picture_filename_with_path)

    post.submit_post(user_id, filter_sql_str_argument(post_data.name), post_data.type, post_data.volume,
                     filter_sql_str_argument(post_data.review), picture_filename)

    return "success", 200


@app.post("/user/profile-picture/{user_token}")
def set_profile_picture(user_token, file: UploadFile):
    user_id = try_to_login_with_token(user_token)

    if file.content_type != "image/jpeg":
        raise HTTPException(400, "wrong format, please upload jpeg")

    filename_construction = str(datetime.now()) + str(user_id)
    filename = sha256(filename_construction.encode('utf-8')).hexdigest()
    filename_with_path = os.path.join("profile_pictures", filename)

    with open(filename_with_path, "wb") as temp_file:
        temp_file.write(file.file.read())

    with Image.open(filename_with_path) as image:
        try:
            image.verify()
        except Exception as e:
            os.remove(filename_with_path)
            raise HTTPException(400, "corrupted picture") from e

        image.thumbnail((512, 512), Image.ANTIALIAS)
        image.save(filename_with_path + ".jpg", 'JPEG', quality=70)

    os.remove(filename_with_path)

    user.set_profile_picture(user_id, filename)

    return filename
