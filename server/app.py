from flask import Flask, request, render_template, redirect, make_response
import uuid
import base64

# import random
import jwt
import time

# import toml
import bcrypt
from functools import wraps
import zipfile
from os import path, getcwd, makedirs, getenv
from pymongo import MongoClient

MAX_UPLOAD_SIZE = 10 * 1024 * 1024

app = Flask(__name__)

app.static_folder = "static"

client = MongoClient(getenv("MONGO_URL", None))
db = client.user_db
users = db.users


def login_required():
    def _login_required(f):
        @wraps(f)
        def __login_required(*args, **kwargs):
            token = request.cookies.get("token")
            if not token:
                return redirect("/login")
            user = verify_token(token)
            if not user:
                return redirect("/login")
            return f(*args, **kwargs, user=user)

        return __login_required

    return _login_required


secret = getenv("SECRET_KEY")

if secret is None:
    print("No secret found, using random bytes")
    secret = uuid.uuid4().bytes
else:
    print("Using secret from env")
    secret = secret.encode()


def generate_token(id, username):
    return jwt.encode({"id": id, "username": username}, secret, algorithm="HS256")


def verify_token(token):
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except:
        return None


@app.route("/static/<path:path>")
def static_file(filename):
    return app.send_static_file(filename)


@app.route("/")
# @login_required()
def index():
    return render_template("index.jinja")


@app.route("/login", methods=["GET"])
def get_login():
    return render_template("login.jinja")


@app.route("/login", methods=["POST"])
def post_login():
    username = request.form["username"]
    password = request.form["password"].encode("utf-8")

    this_user = users.find_one({"username": username})
    if this_user is not None:
        hashed = base64.b64decode(this_user["password"].encode("utf-8"))
        if bcrypt.checkpw(password, hashed):
            resp = make_response(redirect("/"))
            resp.set_cookie("token", generate_token(this_user["id"], username))

            return resp

    return redirect("/login?msg=Invalid+username+or+password")


@app.route("/register", methods=["GET"])
def get_register():
    return render_template("register.jinja")


@app.route("/register", methods=["POST"])
def post_register():
    username = request.form["username"]
    password = request.form["password"].encode("utf-8")

    if users.find_one({"username": username}) is not None:
        return redirect("/register?msg=Please+pick+a+different+username")

    user_id = str(uuid.uuid4())
    users.insert_one(
        {
            "id": user_id,
            "username": username,
            "password": base64.b64encode(
                bcrypt.hashpw(password, bcrypt.gensalt())
            ).decode(),
        }
    )

    res = make_response(redirect("/"))
    res.set_cookie("token", generate_token(user_id, username))
    return res


@app.route("/help")
def get_help():
    return render_template("help.jinja")


@app.route("/upload", methods=["GET"])
@login_required()
def get_upload(user):
    return render_template("upload.jinja", username=user["username"])


@app.route("/upload", methods=["POST"])
@login_required()
def post_upload(user):
    print(request.url)
    if "file" not in request.files:
        return redirect(request.url + "?err=No+file+provided")
    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url + "?err=No+file+provided")
    if file:
        try:
            with zipfile.ZipFile(file) as z:
                size = sum(zinfo.file_size for zinfo in z.filelist)
                if size > MAX_UPLOAD_SIZE:
                    return redirect(request.url + "?err=File+too+large")
                print(user)
                folder = path.join(
                    getcwd(), "uploads", user["id"], time.strftime(
                        "%Y-%m-%d_%H-%M-%S")
                )
                makedirs(folder, exist_ok=True)
                z.extractall(folder)
        except (zipfile.BadZipFile, ValueError) as e:
            return redirect(request.url + "?err=Bad+zip+file")
        # file.save(path.join(getcwd(), f"uploads/{user['id']}"))
    return redirect("/play")


@app.route("/play")
def play():
    return "WIP", 200


if __name__ == "__main__":
    app.run(debug=True)
